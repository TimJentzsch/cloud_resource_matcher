import tempfile
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional, Dict, Tuple, Self

import pulp
from pulp import LpProblem, LpAffineExpression, LpVariable, LpMinimize, LpInteger, LpBinary, lpSum, LpStatus

from optimizer.optimizer_toolbox_model import BaseData, PerformanceData, MultiCloudData, NetworkData
from optimizer.optimizer_toolbox_model.data import VirtualMachine, Service, TimeUnit, Cost
from optimizer.optimizer_toolbox_model.data.network_data import Location
from optimizer.optimizer_toolbox_model.validated import Validated
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


class Model:
    """The model for the cloud computing cost optimization problem."""

    prob: LpProblem
    objective: LpAffineExpression

    base_data: BaseData
    perf_data: Optional[PerformanceData] = None
    multi_data: Optional[MultiCloudData] = None
    network_data: Optional[NetworkData] = None

    # Which virtual machine to put on which service
    vm_matching: Dict[Tuple[VirtualMachine, Service, TimeUnit], LpVariable]
    # The number of instances to buy of each service
    service_instance_count: dict[tuple[Service, TimeUnit], LpVariable]

    def __init__(self, validated_base_data: Validated[BaseData]):
        """Create a new model for the cost optimization problem."""
        base_data = validated_base_data.data
        self.base_data = base_data
        self.prob = LpProblem("cloud_cost_optimization", LpMinimize)

        # The virtual machines that can use service s
        service_virtual_machines: dict[Service, set[VirtualMachine]] = {
            s: set(
                vm
                for vm in base_data.virtual_machines
                if s in base_data.virtual_machine_services[vm]
            )
            for s in base_data.services
        }

        # Assign virtual machine v to cloud service s at time t?
        self.vm_matching = {
            (v, s, t): LpVariable(
                f"vm_matching({v},{s},{t})", cat=LpInteger, lowBound=0
            )
            for v in base_data.virtual_machines
            for s in base_data.virtual_machine_services[v]
            for t in base_data.time
        }

        # Buy how many services instances for s at time t?
        self.service_instance_count = {
            (s, t): LpVariable(
                f"service_instance_count({s},{t})", cat=LpInteger, lowBound=0
            )
            for s in self.base_data.services
            for t in base_data.time
        }

        # Has service s been purchased at time t at all?
        self.service_used = {
            (s, t): LpVariable(f"service_used({s},{t})", cat=LpBinary)
            for s in self.base_data.services
            for t in base_data.time
        }

        # Enforce limits for service instance count
        for s, max_instances in base_data.max_service_instances.items():
            for t in base_data.time:
                self.prob += (
                    self.service_instance_count[s, t] <= max_instances,
                    f"max_service_instances({s},{t})",
                )

        # Calculate service_used
        for s in base_data.services:
            for t in base_data.time:
                self.prob += (
                    self.service_used[s, t] <= self.service_instance_count[s, t],
                    f"connect_service_instances_and_service_used({s},{t})",
                )

        # Satisfy virtual machine demand
        for v in base_data.virtual_machines:
            for t in base_data.time:
                self.prob += (
                    lpSum(
                        self.vm_matching[v, s, t]
                        for s in base_data.virtual_machine_services[v]
                    )
                    == base_data.virtual_machine_demand[v, t],
                    f"virtual_machine_demand({v},{t})",
                )

        # Only assign VMs to services that have been bought
        for s in base_data.services:
            for t in base_data.time:
                self.prob += (
                    lpSum(
                        self.vm_matching[vm, s, t] for vm in service_virtual_machines[s]
                    )
                    <= self.service_used[s, t]
                    * sum(
                        base_data.virtual_machine_demand[vm, t]
                        for vm in service_virtual_machines[s]
                    ),
                    f"vms_to_bought_service({s},{t})",
                )

        # Base costs for used services
        self.objective = LpAffineExpression(
            lpSum(
                self.service_instance_count[s, t] * base_data.service_base_costs[s]
                for s in base_data.services
                for t in base_data.time
            )
        )

    def with_performance(self, validated_perf_data: Validated[PerformanceData]) -> Self:
        """Add performance data to the model."""
        perf_data = validated_perf_data.data
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

        # Enforce performance limits for every service at every point in time
        for s in self.base_data.services:
            for t in self.base_data.time:
                # RAM
                self.prob += (
                    lpSum(
                        self.vm_matching[v, s, t] * perf_data.virtual_machine_min_ram[v]
                        for v in service_virtual_machines[s]
                        if v in perf_data.virtual_machine_min_ram.keys()
                    )
                    <= perf_data.service_ram[s] * self.service_instance_count[s, t],
                    f"ram_performance_limit({s},{t})",
                )

                # vCPUs
                self.prob.addConstraint(
                    lpSum(
                        self.vm_matching[v, s, t]
                        * perf_data.virtual_machine_min_cpu_count[v]
                        for v in service_virtual_machines[s]
                        if v in perf_data.virtual_machine_min_cpu_count.keys()
                    )
                    <= perf_data.service_cpu_count[s]
                    * self.service_instance_count[s, t],
                    f"cpu_performance_limit({s},{t})",
                )

        return self

    def with_multi_cloud(self, validated_multi_data: Validated[MultiCloudData]) -> Self:
        """Add multi cloud data to the model."""
        multi_data = validated_multi_data.data
        self.multi_data = multi_data

        # Is cloud service provider k used at all?
        csp_used = {
            k: LpVariable(f"csp_used({k})", cat=LpBinary)
            for k in multi_data.cloud_service_providers
        }

        # Calculate csp_used values
        for k in multi_data.cloud_service_providers:
            used_service_count = lpSum(
                self.vm_matching[v, s, t]
                for v in self.base_data.virtual_machines
                for s in multi_data.cloud_service_provider_services[k]
                if s in self.base_data.virtual_machine_services[v]
                for t in self.base_data.time
            )

            self.prob += (
                csp_used[k] - used_service_count <= 0,
                f"csp_used({k})_enforce_0",
            )
            self.prob += (
                (
                    csp_used[k]
                    * len(self.base_data.virtual_machines)
                    * len(self.base_data.time)
                    - used_service_count
                )
                >= 0,
                f"csp_used({k})_enforce_1",
            )

        # Enforce minimum and maximum number of used CSPs
        for k in multi_data.cloud_service_providers:
            self.prob.addConstraint(
                lpSum(csp_used[k] for k in multi_data.cloud_service_providers)
                >= multi_data.min_cloud_service_provider_count,
                f"min_cloud_service_provider_count({k})",
            )
            self.prob.addConstraint(
                lpSum(csp_used[k] for k in multi_data.cloud_service_providers)
                <= multi_data.max_cloud_service_provider_count,
                f"max_cloud_service_provider_count({k})",
            )

        return self

    def with_network(self, validated_network_data: Validated[NetworkData]) -> Self:
        """Add network data to the model."""
        network_data = validated_network_data.data
        self.network_data = network_data

        # How many VMs v are located at location loc at time t?
        vm_locations: dict[tuple[VirtualMachine, Location, TimeUnit], LpVariable] = {
            (v, loc, t): LpVariable(
                f"vm_location({v},{loc},{t})", cat=LpInteger, lowBound=0
            )
            for v in self.base_data.virtual_machines
            for loc in network_data.locations
            for t in self.base_data.time
        }

        # All VMs are placed at exactly one location
        for v in self.base_data.virtual_machines:
            for t in self.base_data.time:
                self.prob += (
                    lpSum(vm_locations[v, loc, t] for loc in network_data.locations)
                    == self.base_data.virtual_machine_demand[v, t]
                )

        # The VMs location is the location of the service where it's placed
        for v in self.base_data.virtual_machines:
            for loc in network_data.locations:
                for t in self.base_data.time:
                    for s in self.base_data.virtual_machine_services[v]:
                        if loc in network_data.service_location[s]:
                            self.prob += (
                                vm_locations[v, loc, t] >= self.vm_matching[v, s, t]
                            )

        # Pay for VM -> location traffic
        self.objective += lpSum(
            vm_locations[vm, vm_loc, t]
            * traffic
            * network_data.location_traffic_cost[vm_loc, loc]
            for (
                vm,
                loc,
            ), traffic in network_data.virtual_machine_location_traffic.items()
            for vm_loc in network_data.locations
            for t in self.base_data.time
        )

        # === virtual_machine_virtual_machine_traffic ===

        # The number of vm1 -> vm2 connections where vm1 is at loc1 and vm2 is at loc2 (at time t)
        vm_vm_locations: dict[
            tuple[VirtualMachine, VirtualMachine, Location, Location, TimeUnit],
            LpVariable,
        ] = {
            (vm1, vm2, loc1, loc2, t): LpVariable(
                f"vm_vm_locations({vm1},{vm2},{loc1},{loc2},{t})",
                cat=LpInteger,
                lowBound=0,
            )
            for (
                vm1,
                vm2,
            ) in network_data.virtual_machine_virtual_machine_traffic.keys()
            for loc1 in network_data.locations
            for loc2 in network_data.locations
            for t in self.base_data.time
        }

        # The connections must be at the locations where the VMs are actually placed
        for t in self.base_data.time:
            for (
                vm1,
                vm2,
            ) in network_data.virtual_machine_virtual_machine_traffic.keys():
                # Make enough outgoing connections from each location
                for loc1 in network_data.locations:
                    self.prob += vm_locations[vm1, loc1, t] == lpSum(
                        vm_vm_locations[vm1, vm2, loc1, loc2, t]
                        for loc2 in network_data.locations
                    )

                # Have at least one VM at the incoming location
                for loc1 in network_data.locations:
                    for loc2 in network_data.locations:
                        self.prob += (
                            vm_locations[vm2, loc2, t]
                            * self.base_data.virtual_machine_demand[vm1, t]
                            >= vm_vm_locations[vm1, vm2, loc1, loc2, t]
                        )

        # Respect maximum latencies
        for t in self.base_data.time:
            # For VM -> location traffic
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
                            self.prob += vm_locations[vm1, loc1, t] == 0

            # For VM -> VM traffic
            for (
                vm1,
                vm2,
            ), max_latency in (
                network_data.virtual_machine_virtual_machine_max_latency.items()
            ):
                for loc1 in network_data.locations:
                    for loc2 in network_data.locations:
                        if network_data.location_latency[loc1, loc2] > max_latency:
                            self.prob += vm_vm_locations[vm1, vm2, loc1, loc2, t] == 0

        # Pay for VM -> location traffic caused by VM -> VM connections
        self.objective += lpSum(
            vm_vm_locations[vm1, vm2, loc1, loc2, t]
            * traffic
            * network_data.location_traffic_cost[loc1, loc2]
            for (
                vm1,
                vm2,
            ), traffic in network_data.virtual_machine_virtual_machine_traffic.items()
            for loc1 in network_data.locations
            for loc2 in network_data.locations
            for t in self.base_data.time
        )

        return self

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: Optional[timedelta] = None,
        cost_gap_abs: Optional[Cost] = None,
        cost_gap_rel: Optional[float] = None,
    ) -> SolveSolution:
        """Solve the optimization problem.

        :param solver: The solver to use to solve the mixed-integer program.
        :param time_limit: The maximum amount of time after which to stop the optimization.
        :param cost_gap_abs: The absolute cost tolerance for the solver to stop.
        :param cost_gap_rel: The relative cost tolerance for the solver to stop as a fraction.
        Must be a value between 0.0 and 1.0.
        """
        # Add the objective function
        self.prob.setObjective(self.objective)

        pulp_solver = get_pulp_solver(
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=cost_gap_abs,
            cost_gap_rel=cost_gap_rel,
        )

        # Solve the problem
        status_code = self.prob.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)

        # Extract the solution
        vm_service_matching: VmServiceMatching = {}

        for v in self.base_data.virtual_machines:
            for s in self.base_data.virtual_machine_services[v]:
                for t in self.base_data.time:
                    value = round(pulp.value(self.vm_matching[v, s, t]))

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in self.base_data.services:
            for t in self.base_data.time:
                value = round(pulp.value(self.service_instance_count[s, t]))

                if value >= 1:
                    service_instance_count[s, t] = value

        cost = self.prob.objective.value()
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
            self.prob.writeLP(filename=file.name)
            return "".join(file.readlines()[:line_limit])
