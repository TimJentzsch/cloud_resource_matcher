from dataclasses import dataclass
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


@dataclass
class Solution:
    vm_service_matching: Dict[VirtualMachine, Service]
    cost: float


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
            for s in base_data.services
        }

        # Assign each VM to exactly one cloud service
        for v in base_data.virtual_machines:
            self.prob += lpSum(self.vm_matching[v, s] for s in base_data.services) == 1

        # Base costs for used virtual machines
        self.objective = lpSum(
            self.vm_matching[v, s] * base_data.service_base_costs[s]
            for v in base_data.virtual_machines
            for s in base_data.services
        )

    def with_performance(self, perf_data: PerformanceData) -> Self:
        """Add performance data to the model."""
        self.perf_data = perf_data

        # Enforce performance limits of services
        for s in self.base_data.services:
            pass
            # RAM
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.virtual_machine_min_ram[v]
                    for v in self.base_data.virtual_machines
                )
                <= perf_data.service_ram[s]
            )
            # vCPUs
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.virtual_machine_min_cpu_count[v]
                    for v in self.base_data.virtual_machines
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
            )
            self.prob += csp_used[k] <= used_service_count
            self.prob += (
                csp_used[k] * len(self.base_data.virtual_machines)
                >= used_service_count
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

    def solve(self) -> Solution:
        """Solve the optimization problem."""
        # Add the objective function
        self.prob += self.objective

        # Solve the problem
        status_code = self.prob.solve()
        status = LpStatus[status_code]

        if status != "Optimal":
            # TODO: Handle this in a better way, e.g. a custom exception
            raise RuntimeError(f"Could not optimize problem, status {status}")

        vm_service_matching: Dict[VirtualMachine, Service] = {}

        # Extract the solution
        for v in self.base_data.virtual_machines:
            for s in self.base_data.services:
                if pulp.value(self.vm_matching[v, s]) == 1:
                    vm_service_matching[v] = s

        cost = self.prob.objective.value()
        solution = Solution(vm_service_matching=vm_service_matching, cost=cost)

        return solution
