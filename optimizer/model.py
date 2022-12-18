from typing import Dict, Optional, Self

from pulp import LpVariable, LpProblem, LpMinimize, lpSum, LpAffineExpression, LpBinary

from optimizer.data import (
    BaseData,
    VirtualMachine,
    Service,
    PerformanceData,
    MultiCloudData,
)


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

        # Enforce minimum performance constraints
        for v in self.base_data.virtual_machines:
            # RAM
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.service_ram[s]
                    for s in self.base_data.services
                )
                >= perf_data.virtual_machine_min_ram[v]
            )
            # vCPUs
            self.prob += (
                lpSum(
                    self.vm_matching[v, s] * perf_data.service_cpu_count[s]
                    for s in self.base_data.services
                )
                >= perf_data.virtual_machine_min_cpu_count[v]
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
                csp_used[k] * len(multi_data.cloud_service_provider_services)
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

    def solve(self) -> LpProblem:
        """Solve the optimization problem."""
        # Add the objective function
        self.prob += self.objective

        self.prob.solve()
        return self.prob
