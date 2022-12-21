from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Self

import pulp
from pulp import (
    LpVariable,
    LpProblem,
    LpMinimize,
    lpSum,
    LpAffineExpression,
    LpBinary,
    LpStatus,
)

from optimizer.data import (
    BaseData,
    VirtualMachine,
    Service,
    PerformanceData,
    MultiCloudData,
)
from optimizer.solver import Solver


@dataclass
class SolveSolution:
    vm_service_matching: Dict[VirtualMachine, Service]
    cost: float


class SolveErrorReason(Enum):
    INFEASIBLE = 0


class SolveError(RuntimeError):
    reason: SolveErrorReason

    def __init__(self, reason: SolveErrorReason):
        super().__init__(f"Could not solve optimization problem: {reason}")
        self.reason = reason


class Model:
    """The model for the cloud computing cost optimization problem."""

    prob: LpProblem
    objective: LpAffineExpression

    base_data: BaseData
    perf_data: Optional[PerformanceData]
    multi_data: Optional[MultiCloudData]

    vm_matching: Dict[(VirtualMachine, Service)]

    def __init__(self, base_data: BaseData):
        """Create a new model for the cost optimization problem."""
        self.base_data = base_data
        self.prob = LpProblem("cloud_cost_optimization", LpMinimize)

        # Assign virtual machine v to cloud service s?
        self.vm_matching = {
            (v, s): LpVariable(f"vm_matching[{v},{s}]", cat=LpBinary)
            for v in base_data.virtual_machines
            for s in base_data.virtual_machine_services[v]
        }

        # Assign each VM to exactly one cloud service
        for v in base_data.virtual_machines:
            self.prob += (
                lpSum(
                    self.vm_matching[v, s]
                    for s in base_data.virtual_machine_services[v]
                )
                == 1
            )

        # Base costs for used virtual machines
        self.objective = lpSum(
            self.vm_matching[v, s] * base_data.service_base_costs[s]
            for v in base_data.virtual_machines
            for s in base_data.virtual_machine_services[v]
        )

    def with_performance(self, perf_data: PerformanceData) -> Self:
        """Add performance data to the model."""
        self.perf_data = perf_data

        # Compute which services can host which virtual machines
        service_virtual_machines = {
            s: [
                v
                for v in self.base_data.virtual_machines
                if s in self.base_data.virtual_machine_services[v]
            ]
            for s in self.base_data.services
        }

        # Enforce performance limits of services
        for s in self.base_data.services:
            pass
            # RAM
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.virtual_machine_min_ram[v]
                    for v in service_virtual_machines[s]
                )
                <= perf_data.service_ram[s]
            )
            # vCPUs
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.virtual_machine_min_cpu_count[v]
                    for v in service_virtual_machines[s]
                )
                <= perf_data.service_cpu_count[s]
            )

        return self

    def with_multi_cloud(self, multi_data: MultiCloudData) -> Self:
        """Add multi cloud data to the model."""
        self.multi_data = multi_data

        # Is cloud service provider k used at all?
        csp_used = {
            k: LpVariable(f"csp_used[{k}]", cat=LpBinary)
            for k in multi_data.cloud_service_providers
        }

        # Calculate csp_used values
        for k in multi_data.cloud_service_providers:
            used_service_count = lpSum(
                self.vm_matching[v, s]
                for v in self.base_data.virtual_machines
                for s in multi_data.cloud_service_provider_services[k]
                if s in self.base_data.virtual_machine_services[v]
            )
            self.prob += csp_used[k] <= used_service_count
            self.prob += (
                csp_used[k] * len(self.base_data.virtual_machines) >= used_service_count
            )

        # Enforce minimum and maximum number of used CSPs
        self.prob += (
            lpSum(csp_used[k] for k in multi_data.cloud_service_providers)
            >= multi_data.min_cloud_service_provider_count
        )
        self.prob += (
            lpSum(csp_used[k] for k in multi_data.cloud_service_providers)
            <= multi_data.max_cloud_service_provider_count
        )

        return self

    def solve(self, solver: Solver = Solver.DEFAULT) -> SolveSolution:
        """Solve the optimization problem."""
        # Add the objective function
        self.prob += self.objective

        if solver == Solver.GUROBI:
            pulp_solver = pulp.GUROBI_CMD()
        else:
            pulp_solver = None

        # Solve the problem
        status_code = self.prob.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)

        vm_service_matching: Dict[VirtualMachine, Service] = {}

        # Extract the solution
        for v in self.base_data.virtual_machines:
            for s in self.base_data.services:
                if pulp.value(self.vm_matching[v, s]) == 1:
                    vm_service_matching[v] = s

        cost = self.prob.objective.value()
        solution = SolveSolution(vm_service_matching=vm_service_matching, cost=cost)

        return solution
