from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpBinary, LpVariable, lpSum

from optimizer.data import BaseData, MultiCloudData
from optimizer.data.types import CloudServiceProvider
from .base import BaseMipData
from optimizer.optimizer.extension import Extension


@dataclass
class MultiCloudMipData:
    var_csp_used: dict[CloudServiceProvider, LpVariable]


class BuildMipMultiCloudExt(Extension[MultiCloudMipData]):
    base_data: BaseData
    multi_cloud_data: MultiCloudData
    base_mip_data: BaseMipData
    problem: LpProblem
    objective: LpAffineExpression

    def __init__(
        self,
        base_data: BaseData,
        multi_cloud_data: MultiCloudData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
        objective: LpAffineExpression,
    ):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data
        self.base_mip_data = base_mip_data
        self.problem = problem
        self.objective = objective

    def action(self) -> MultiCloudMipData:
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
                for s in self.multi_cloud_data.cloud_service_provider_services[k]
                if s in self.base_data.virtual_machine_services[v]
            )

            self.problem += (
                var_csp_used[k] <= used_service_count,
                f"csp_used({k})_enforce_0",
            )
            self.problem += (
                (var_csp_used[k] * len(self.base_data.virtual_machines)) >= used_service_count,
                f"csp_used({k})_enforce_1",
            )

        # Enforce minimum and maximum number of used CSPs
        for k in self.multi_cloud_data.cloud_service_providers:
            self.problem.addConstraint(
                lpSum(var_csp_used[k] for k in self.multi_cloud_data.cloud_service_providers)
                >= self.multi_cloud_data.min_cloud_service_provider_count,
                f"min_cloud_service_provider_count({k})",
            )
            self.problem.addConstraint(
                lpSum(var_csp_used[k] for k in self.multi_cloud_data.cloud_service_providers)
                <= self.multi_cloud_data.max_cloud_service_provider_count,
                f"max_cloud_service_provider_count({k})",
            )

        return MultiCloudMipData(var_csp_used)
