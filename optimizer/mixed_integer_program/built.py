import tempfile
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

import pulp
from pulp import LpProblem, LpStatus

from optimizer.mixed_integer_program import MixedIntegerProgram, VarVmServiceMatching, VarServiceInstanceCount
from optimizer.optimizer_toolbox_model.data import VirtualMachine, Service, TimeUnit, Cost
from optimizer.solver import Solver, get_pulp_solver

VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]


@dataclass
class SolveSolution:
    vm_service_matching: VmServiceMatching
    service_instance_count: ServiceInstanceCount
    cost: float


class SolveErrorReason(Enum):
    INFEASIBLE = 0


class SolveError(RuntimeError):
    reason: SolveErrorReason

    def __init__(self, reason: SolveErrorReason):
        super().__init__(f"Could not solve optimization problem: {reason}")
        self.reason = reason


class BuiltMixedIntegerProgram:
    mixed_integer_program: MixedIntegerProgram
    problem: LpProblem

    vm_matching: VarVmServiceMatching
    service_instance_count: VarServiceInstanceCount

    def __init__(
        self,
        mixed_integer_program: MixedIntegerProgram,
        problem: LpProblem,
        vm_matching,
        service_instance_count,
    ):
        """
        Create a new built Mixed Integer Program.

        This should not be constructed manually, instead use `MixedIntegerProgram.build()`.
        """
        self.mixed_integer_program = mixed_integer_program
        self.problem = problem
        self.vm_matching = vm_matching
        self.service_instance_count = service_instance_count

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> SolveSolution:
        """Solve the optimization problem.

        :param solver: The solver to use to solve the mixed-integer program.
        :param time_limit: The maximum amount of time after which to stop the optimization.
        :param cost_gap_abs: The absolute cost tolerance for the solver to stop.
        :param cost_gap_rel: The relative cost tolerance for the solver to stop as a fraction.
        Must be a value between 0.0 and 1.0.
        """
        pulp_solver = get_pulp_solver(
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=cost_gap_abs,
            cost_gap_rel=cost_gap_rel,
        )

        # Solve the problem
        status_code = self.problem.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)

        # Extract the solution
        vm_service_matching: VmServiceMatching = {}

        base_data = self.mixed_integer_program.optimizer_toolbox_model.base_data

        for v in base_data.virtual_machines:
            for s in base_data.virtual_machine_services[v]:
                for t in base_data.time:
                    value = round(pulp.value(self.vm_matching[v, s, t]))

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in base_data.services:
            for t in base_data.time:
                value = round(pulp.value(self.service_instance_count[s, t]))

                if value >= 1:
                    service_instance_count[s, t] = value

        cost = self.problem.objective.value()
        solution = SolveSolution(
            vm_service_matching=vm_service_matching,
            service_instance_count=service_instance_count,
            cost=cost,
        )

        return solution

    def get_lp_string(self, line_limit: int = 100) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="utf-8", suffix=".lp"
        ) as file:
            self.problem.writeLP(filename=file.name)
            return "".join(file.readlines()[:line_limit])
