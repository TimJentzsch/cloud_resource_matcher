import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Self, Tuple

import pulp
from pulp import (
    LpVariable,
    LpProblem,
    LpMinimize,
    lpSum,
    LpAffineExpression,
    LpBinary,
    LpStatus,
    LpInteger,
    LpConstraint,
    LpConstraintLE,
    LpConstraintGE,
    LpConstraintEQ,
)

from optimizer.data import (
    VirtualMachine,
    Service,
    TimeUnit,
)
from optimizer.data.base_data import BaseData
from optimizer.data.multi_cloud_data import MultiCloudData
from optimizer.data.network_data import NetworkData
from optimizer.data.performance_data import PerformanceData
from optimizer.data.validated import Validated
from optimizer.solver import Solver


VmServiceMatching = Dict[Tuple[VirtualMachine, Service, TimeUnit], int]


@dataclass
class SolveSolution:
    vm_service_matching: VmServiceMatching
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

    vm_matching: Dict[Tuple[VirtualMachine, Service, TimeUnit], LpVariable]

    def __init__(self, validated_base_data: Validated[BaseData]):
        """Create a new model for the cost optimization problem."""
        base_data = validated_base_data.data
        self.base_data = base_data
        self.prob = LpProblem("cloud_cost_optimization", LpMinimize)

        # Assign virtual machine v to cloud service s at time t?
        self.vm_matching = {
            (v, s, t): LpVariable(
                f"vm_matching({v},{s},{t})", cat=LpInteger, lowBound=0
            )
            for v in base_data.virtual_machines
            for s in base_data.virtual_machine_services[v]
            for t in base_data.time
        }

        # Satisfy virtual machine demand
        for v in base_data.virtual_machines:
            for t in base_data.time:
                self.prob.addConstraint(
                    LpConstraint(
                        lpSum(
                            self.vm_matching[v, s, t]
                            for s in base_data.virtual_machine_services[v]
                        ),
                        sense=LpConstraintEQ,
                        rhs=base_data.virtual_machine_demand[v, t],
                    ),
                    f"virtual_machine_demand({v},{t})",
                )

        # Base costs for used virtual machines
        self.objective = LpAffineExpression(
            lpSum(
                self.vm_matching[v, s, t] * base_data.service_base_costs[s]
                for v in base_data.virtual_machines
                for s in base_data.virtual_machine_services[v]
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
                self.prob.addConstraint(
                    LpConstraint(
                        lpSum(
                            self.vm_matching[v, s, t]
                            * perf_data.virtual_machine_min_ram[v]
                            for v in service_virtual_machines[s]
                            if v in perf_data.virtual_machine_min_ram.keys()
                        ),
                        sense=LpConstraintLE,
                        rhs=perf_data.service_ram[s],
                    ),
                    f"ram_performance_limit({s},{t})",
                )

                # vCPUs
                self.prob.addConstraint(
                    LpConstraint(
                        lpSum(
                            self.vm_matching[v, s, t]
                            * perf_data.virtual_machine_min_cpu_count[v]
                            for v in service_virtual_machines[s]
                            if v in perf_data.virtual_machine_min_cpu_count.keys()
                        ),
                        sense=LpConstraintLE,
                        rhs=perf_data.service_cpu_count[s],
                    ),
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

            self.prob.addConstraint(
                LpConstraint(
                    csp_used[k] - used_service_count, sense=LpConstraintLE, rhs=0
                ),
                f"csp_used({k})_enforce_0",
            )
            self.prob.addConstraint(
                LpConstraint(
                    csp_used[k]
                    * len(self.base_data.virtual_machines)
                    * len(self.base_data.time)
                    - used_service_count,
                    sense=LpConstraintGE,
                    rhs=0,
                ),
                f"csp_used({k})_enforce_1",
            )

        # Enforce minimum and maximum number of used CSPs
        for k in multi_data.cloud_service_providers:
            self.prob.addConstraint(
                LpConstraint(
                    lpSum(csp_used[k] for k in multi_data.cloud_service_providers),
                    sense=LpConstraintGE,
                    rhs=multi_data.min_cloud_service_provider_count,
                ),
                f"min_cloud_service_provider_count({k})",
            )
            self.prob.addConstraint(
                LpConstraint(
                    lpSum(csp_used[k] for k in multi_data.cloud_service_providers),
                    sense=LpConstraintLE,
                    rhs=multi_data.max_cloud_service_provider_count,
                ),
                f"max_cloud_service_provider_count({k})",
            )

        return self

    def with_network(self, validated_network_data: Validated[NetworkData]) -> Self:
        """Add network data to the model."""
        network_data = validated_network_data.data
        self.network_data = network_data

        # How many VMs v are located at location loc at time t?
        vm_locations = {
            (v, loc, t): LpVariable(f"vm_location({v},{loc},{t})", cat=LpInteger)
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
            * network_data.location_traffic_cost[vm_loc, loc]
            for (
                vm,
                loc,
            ), traffic in network_data.virtual_machine_location_traffic.items()
            for vm_loc in network_data.locations
            for t in self.base_data.time
        )

        return self

    def solve(self, solver: Solver = Solver.DEFAULT) -> SolveSolution:
        """Solve the optimization problem."""
        # Add the objective function
        self.prob.setObjective(self.objective)

        if solver == Solver.GUROBI:
            pulp_solver = pulp.GUROBI_CMD()
        else:
            pulp_solver = None

        # Solve the problem
        status_code = self.prob.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)

        vm_service_matching: VmServiceMatching = {}

        # Extract the solution
        for v in self.base_data.virtual_machines:
            for s in self.base_data.virtual_machine_services[v]:
                for t in self.base_data.time:
                    value = round(pulp.value(self.vm_matching[v, s, t]))

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        cost = self.prob.objective.value()
        solution = SolveSolution(vm_service_matching=vm_service_matching, cost=cost)

        return solution

    def get_lp_string(self, line_limit: int = 100) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="utf-8", suffix=".lp"
        ) as file:
            self.prob.writeLP(filename=file.name)
            return "".join(file.readlines()[:line_limit])
