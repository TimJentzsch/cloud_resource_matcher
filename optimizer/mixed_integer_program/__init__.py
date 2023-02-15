import tempfile
from datetime import timedelta

import pulp
from pulp import (
    LpProblem,
    LpAffineExpression,
    LpVariable,
    LpMinimize,
    LpBinary,
    lpSum,
    LpStatus,
)

from optimizer.mixed_integer_program.types import (
    VarVmServiceMatching,
    ServiceVirtualMachines,
    VmServiceMatching,
    ServiceInstanceCount,
)
from optimizer.mixed_integer_program.solving import (
    SolveSolution,
    SolveError,
    SolveErrorReason,
)
from optimizer.optimizer_toolbox_model import (
    ValidatedOptimizerToolboxModel,
    OptimizerToolboxModel,
)
from optimizer.optimizer_toolbox_model.data import (
    VirtualMachine,
    Cost,
    Service,
)
from optimizer.optimizer_toolbox_model.data.network_data import Location
from optimizer.solver import Solver, get_pulp_solver


class MixedIntegerProgram:
    """The model for the cloud computing cost optimization problem."""

    optimizer_toolbox_model: OptimizerToolboxModel

    def __init__(
        self, validated_optimizer_toolbox_model: ValidatedOptimizerToolboxModel
    ):
        """Create a mixed integer program for the cloud cost optimization model."""
        self.optimizer_toolbox_model = (
            validated_optimizer_toolbox_model.optimizer_toolbox_model
        )

    def build(self) -> "BuiltMixedIntegerProgram":
        """Build the mixed integer program from the given optimizer toolbox model."""
        base_data = self.optimizer_toolbox_model.base_data

        problem = LpProblem("cloud_cost_optimization", LpMinimize)

        # Pre-compute which services can host which VMs
        service_virtual_machines: ServiceVirtualMachines = {
            s: set(
                vm
                for vm in base_data.virtual_machines
                if s in base_data.virtual_machine_services[vm]
            )
            for s in base_data.services
        }

        # Assign virtual machine v to cloud service s at time t?
        # ASSUMPTION: Each service instance can only be used by one VM instance
        # ASSUMPTION: All instances of one VM have to be deployed
        # on the same service type
        vm_matching: VarVmServiceMatching = {
            (v, s): LpVariable(f"vm_matching({v},{s})", cat=LpBinary)
            for v in base_data.virtual_machines
            for s in base_data.virtual_machine_services[v]
        }

        # Has service s been purchased at all?
        service_used: dict[Service, LpVariable] = {
            s: LpVariable(f"service_used({s})", cat=LpBinary)
            for s in base_data.services
        }

        # Enforce limits for service instance count
        for s, max_instances in base_data.max_service_instances.items():
            for t in base_data.time:
                problem += (
                    lpSum(
                        vm_matching[vm, s] * base_data.virtual_machine_demand[vm, t]
                        for vm in service_virtual_machines[s]
                    )
                    <= max_instances,
                    f"max_service_instances({s},{t})",
                )

        # Calculate service_used
        for s in base_data.services:
            for t in base_data.time:
                problem += (
                    service_used[s]
                    <= lpSum(vm_matching[vm, s] for vm in service_virtual_machines[s]),
                    f"connect_service_instances_and_service_used({s},{t})",
                )

        # Base costs for used services
        objective = LpAffineExpression(
            lpSum(
                vm_matching[vm, s] * base_data.service_base_costs[s]
                for vm in base_data.virtual_machines
                for s in base_data.virtual_machine_services[vm]
            )
        )

        # Add the optional parts of the model, if they are specified
        self._build_performance(self.optimizer_toolbox_model, problem, vm_matching)
        self._build_network(
            self.optimizer_toolbox_model,
            problem,
            objective,
            vm_matching,
        )
        self._build_multi_cloud(
            self.optimizer_toolbox_model,
            problem,
            vm_matching,
        )

        # Set the objective function
        problem.setObjective(objective)

        return BuiltMixedIntegerProgram(
            mixed_integer_program=self,
            problem=problem,
            vm_matching=vm_matching,
            service_virtual_machines=service_virtual_machines,
        )

    @staticmethod
    def _build_performance(
        optimizer_toolbox_model: OptimizerToolboxModel,
        problem: LpProblem,
        vm_matching: VarVmServiceMatching,
    ) -> None:
        """Add the performance data to the problem."""
        base_data = optimizer_toolbox_model.base_data
        performance_data = optimizer_toolbox_model.performance_data

        if performance_data is None:
            return

        # Enforce performance limits for every service
        for vm in base_data.virtual_machines:
            for s in base_data.virtual_machine_services[vm]:
                if vm in performance_data.virtual_machine_min_ram.keys():
                    # RAM
                    problem += (
                        vm_matching[vm, s]
                        * performance_data.virtual_machine_min_ram[vm]
                        <= performance_data.service_ram[s],
                        f"ram_performance_limit({vm},{s})",
                    )

                if vm in performance_data.virtual_machine_min_cpu_count.keys():
                    # vCPUs
                    problem += (
                        vm_matching[vm, s]
                        * performance_data.virtual_machine_min_cpu_count[vm]
                        <= performance_data.service_cpu_count[s],
                        f"cpu_performance_limit({vm},{s})",
                    )

    @staticmethod
    def _build_network(
        optimizer_toolbox_model: OptimizerToolboxModel,
        problem: LpProblem,
        objective: LpAffineExpression,
        vm_matching: VarVmServiceMatching,
    ) -> None:
        base_data = optimizer_toolbox_model.base_data
        network_data = optimizer_toolbox_model.network_data

        if network_data is None:
            return

        # Are the VMs v located at location loc?
        vm_locations: dict[tuple[VirtualMachine, Location], LpVariable] = {
            (v, loc): LpVariable(
                f"vm_location({v},{loc})",
                cat=LpBinary,
            )
            for v in base_data.virtual_machines
            for loc in network_data.locations
        }

        # All VMs are placed at exactly one location
        for v in base_data.virtual_machines:
            problem += (
                lpSum(vm_locations[v, loc] for loc in network_data.locations) == 1,
                f"one_vm_location({v})",
            )

        # The VMs location is the location of the service where it's placed
        for v in base_data.virtual_machines:
            for loc in network_data.locations:
                for s in base_data.virtual_machine_services[v]:
                    if loc in network_data.service_location[s]:
                        problem += vm_locations[v, loc] >= vm_matching[v, s]

        # Pay for VM -> location traffic
        objective += lpSum(
            vm_locations[vm, vm_loc]
            * traffic
            * network_data.location_traffic_cost[vm_loc, loc]
            for (
                vm,
                loc,
            ), traffic in network_data.virtual_machine_location_traffic.items()
            for vm_loc in network_data.locations
        )

        # === virtual_machine_virtual_machine_traffic ===

        # Is there a vm1 -> vm2 connection where vm1 is at loc1
        # and vm2 is at loc2
        vm_vm_locations: dict[
            tuple[VirtualMachine, VirtualMachine, Location, Location],
            LpVariable,
        ] = {
            (vm1, vm2, loc1, loc2): LpVariable(
                f"vm_vm_locations({vm1},{vm2},{loc1},{loc2})",
                cat=LpBinary,
            )
            for (
                vm1,
                vm2,
            ) in network_data.virtual_machine_virtual_machine_traffic.keys()
            for loc1 in network_data.locations
            for loc2 in network_data.locations
        }

        # The connections must be at the locations where the VMs are actually placed
        for (
            vm1,
            vm2,
        ) in network_data.virtual_machine_virtual_machine_traffic.keys():
            # Make enough outgoing connections from each location
            for loc1 in network_data.locations:
                problem += vm_locations[vm1, loc1] == lpSum(
                    vm_vm_locations[vm1, vm2, loc1, loc2]
                    for loc2 in network_data.locations
                )

            # Have at least one VM at the incoming location
            for loc1 in network_data.locations:
                for loc2 in network_data.locations:
                    problem += (
                        vm_locations[vm2, loc2] >= vm_vm_locations[vm1, vm2, loc1, loc2]
                    )

        # Respect maximum latencies for VM -> location traffic
        for (
            vm1,
            loc2,
        ), max_latency in network_data.virtual_machine_location_max_latency.items():
            for loc1 in network_data.locations:
                if network_data.location_latency[loc1, loc2] > max_latency:
                    if (
                        vm1,
                        loc2,
                    ) in network_data.virtual_machine_location_traffic.keys():
                        problem += vm_locations[vm1, loc1] == 0

        # Respect maximum latencies for VM -> VM traffic
        for (
            vm1,
            vm2,
        ), max_latency in (
            network_data.virtual_machine_virtual_machine_max_latency.items()
        ):
            for loc1 in network_data.locations:
                for loc2 in network_data.locations:
                    if network_data.location_latency[loc1, loc2] > max_latency:
                        problem += vm_vm_locations[vm1, vm2, loc1, loc2] == 0

        # Pay for VM -> location traffic caused by VM -> VM connections
        objective += lpSum(
            vm_vm_locations[vm1, vm2, loc1, loc2]
            * traffic
            * network_data.location_traffic_cost[loc1, loc2]
            for (
                vm1,
                vm2,
            ), traffic in network_data.virtual_machine_virtual_machine_traffic.items()
            for loc1 in network_data.locations
            for loc2 in network_data.locations
            for t in base_data.time
        )

    @staticmethod
    def _build_multi_cloud(
        optimizer_toolbox_model: OptimizerToolboxModel,
        problem: LpProblem,
        vm_matching: VarVmServiceMatching,
    ):
        base_data = optimizer_toolbox_model.base_data
        multi_cloud_data = optimizer_toolbox_model.multi_cloud_data

        if multi_cloud_data is None:
            return

        # Is cloud service provider k used at all?
        csp_used = {
            k: LpVariable(f"csp_used({k})", cat=LpBinary)
            for k in multi_cloud_data.cloud_service_providers
        }

        # Calculate csp_used values
        for k in multi_cloud_data.cloud_service_providers:
            used_service_count = lpSum(
                vm_matching[v, s]
                for v in base_data.virtual_machines
                for s in multi_cloud_data.cloud_service_provider_services[k]
                if s in base_data.virtual_machine_services[v]
            )

            problem += (
                csp_used[k] - used_service_count <= 0,
                f"csp_used({k})_enforce_0",
            )
            problem += (
                (
                    csp_used[k] * len(base_data.virtual_machines) * len(base_data.time)
                    - used_service_count
                )
                >= 0,
                f"csp_used({k})_enforce_1",
            )

        # Enforce minimum and maximum number of used CSPs
        for k in multi_cloud_data.cloud_service_providers:
            problem.addConstraint(
                lpSum(csp_used[k] for k in multi_cloud_data.cloud_service_providers)
                >= multi_cloud_data.min_cloud_service_provider_count,
                f"min_cloud_service_provider_count({k})",
            )
            problem.addConstraint(
                lpSum(csp_used[k] for k in multi_cloud_data.cloud_service_providers)
                <= multi_cloud_data.max_cloud_service_provider_count,
                f"max_cloud_service_provider_count({k})",
            )


class BuiltMixedIntegerProgram:
    mixed_integer_program: MixedIntegerProgram
    problem: LpProblem

    vm_matching: VarVmServiceMatching
    service_virtual_machines: ServiceVirtualMachines

    def __init__(
        self,
        mixed_integer_program: MixedIntegerProgram,
        problem: LpProblem,
        vm_matching: VarVmServiceMatching,
        service_virtual_machines: ServiceVirtualMachines,
    ):
        """
        Create a new built Mixed Integer Program.

        This should not be constructed manually,
        instead use `MixedIntegerProgram.build()`.
        """
        self.mixed_integer_program = mixed_integer_program
        self.problem = problem
        self.vm_matching = vm_matching
        self.service_virtual_machines = service_virtual_machines

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> SolveSolution:
        """Solve the optimization problem.

        :param solver: The solver to use to solve the mixed-integer program.
        :param time_limit: The maximum amount of time after which to
        stop the optimization.
        :param cost_gap_abs: The absolute cost tolerance for the solver to stop.
        :param cost_gap_rel: The relative cost tolerance for the solver to stop
        as a fraction. Must be a value between 0.0 and 1.0.
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
                    value = (
                        round(pulp.value(self.vm_matching[v, s]))
                        * base_data.virtual_machine_demand[v, t]
                    )

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in base_data.services:
            for t in base_data.time:
                value = sum(
                    round(pulp.value(self.vm_matching[vm, s]))
                    * base_data.virtual_machine_demand[vm, t]
                    for vm in self.service_virtual_machines[s]
                )

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
