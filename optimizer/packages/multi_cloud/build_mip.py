from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpBinary, LpVariable, lpSum

from optimizer.data import BaseData, MultiCloudData
from optimizer.data.types import CloudServiceProvider
from optimizer.packages.base import BaseMipData
from optiframe import Task


@dataclass
class MultiCloudMipData:
    var_csp_used: dict[CloudServiceProvider, LpVariable]


class BuildMipMultiCloudTask(Task[MultiCloudMipData]):
    base_data: BaseData
    multi_cloud_data: MultiCloudData
    base_mip_data: BaseMipData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        multi_cloud_data: MultiCloudData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def execute(self) -> MultiCloudMipData:
        # Is cloud service provider k used at all?
        var_csp_used: dict[CloudServiceProvider, LpVariable] = {
            k: LpVariable(f"csp_used({k})", cat=LpBinary)
            for k in self.multi_cloud_data.cloud_service_providers
        }

        # Calculate csp_used values
        for k in self.multi_cloud_data.cloud_service_providers:
            used_service_count = lpSum(
                self.base_mip_data.var_vm_matching[v, s]
                for v in self.base_data.virtual_machines
                for s in self.base_data.virtual_machine_services[v]
                if s in self.multi_cloud_data.cloud_service_provider_services[k]
            )

            self.problem += (
                var_csp_used[k] <= used_service_count,
                f"csp_used_enforce_0({k})",
            )

            for vm in self.base_data.virtual_machines:
                for s in self.base_data.virtual_machine_services[vm]:
                    if s in self.multi_cloud_data.cloud_service_provider_services[k]:
                        self.problem += (
                            var_csp_used[k] >= self.base_mip_data.var_vm_matching[vm, s],
                            f"csp_used_enforce_1({k},{vm},{s})",
                        )

        # Enforce minimum and maximum number of used CSPs
        self.problem.addConstraint(
            lpSum(var_csp_used[k] for k in self.multi_cloud_data.cloud_service_providers)
            >= self.multi_cloud_data.min_cloud_service_provider_count,
            "min_cloud_service_provider_count",
        )
        self.problem.addConstraint(
            lpSum(var_csp_used[k] for k in self.multi_cloud_data.cloud_service_providers)
            <= self.multi_cloud_data.max_cloud_service_provider_count,
            "max_cloud_service_provider_count",
        )

        # Add CSP cost to objective
        self.problem.objective += lpSum(
            var_csp_used[k] * self.multi_cloud_data.cloud_service_provider_costs[k]
            for k in self.multi_cloud_data.cloud_service_providers
        )

        return MultiCloudMipData(var_csp_used)
