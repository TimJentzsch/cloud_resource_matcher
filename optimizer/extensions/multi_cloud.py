from dataclasses import dataclass

from pulp import LpVariable, LpBinary, LpAffineExpression, LpProblem, lpSum

from .base import BaseMipData
from .extension import Extension, ExtensionId
from .data import BaseData, MultiCloudData
from optimizer.extensions.decorators import dependencies
from .data.types import CloudServiceProvider


@dataclass
class MultiCloudMipData:
    data: MultiCloudData
    var_csp_used: dict[CloudServiceProvider, LpVariable]


@dataclass
class MultiCloudSolution:
    mip_data: MultiCloudMipData


class MultiCloudExtension(Extension):
    @staticmethod
    def identifier() -> ExtensionId:
        return "multi_cloud"

    @staticmethod
    @dependencies("base")
    def validate(data: MultiCloudData, base: BaseData):
        data.validate(base)

    @staticmethod
    @dependencies("base")
    def extend_mip(
        data: MultiCloudData,
        problem: LpProblem,
        objective: LpAffineExpression,
        base: BaseMipData,
    ) -> MultiCloudMipData:
        # Is cloud service provider k used at all?
        var_csp_used: dict[CloudServiceProvider, LpVariable] = {
            k: LpVariable(f"csp_used({k})", cat=LpBinary)
            for k in data.cloud_service_providers
        }

        # Calculate csp_used values
        for k in data.cloud_service_providers:
            used_service_count = lpSum(
                base.var_vm_matching[v, s]
                for v in base.data.virtual_machines
                for s in data.cloud_service_provider_services[k]
                if s in base.data.virtual_machine_services[v]
            )

            problem += (
                var_csp_used[k] - used_service_count <= 0,
                f"csp_used({k})_enforce_0",
            )
            problem += (
                (
                    var_csp_used[k]
                    * len(base.data.virtual_machines)
                    * len(base.data.time)
                    - used_service_count
                )
                >= 0,
                f"csp_used({k})_enforce_1",
            )

        # Enforce minimum and maximum number of used CSPs
        for k in data.cloud_service_providers:
            problem.addConstraint(
                lpSum(var_csp_used[k] for k in data.cloud_service_providers)
                >= data.min_cloud_service_provider_count,
                f"min_cloud_service_provider_count({k})",
            )
            problem.addConstraint(
                lpSum(var_csp_used[k] for k in data.cloud_service_providers)
                <= data.max_cloud_service_provider_count,
                f"max_cloud_service_provider_count({k})",
            )

        return MultiCloudMipData(data=data, var_csp_used=var_csp_used)

    @staticmethod
    @dependencies()
    def extract_solution(
        mip_data: MultiCloudMipData, problem: LpProblem
    ) -> MultiCloudSolution:
        # TODO: Extract CSP solution
        return MultiCloudSolution(mip_data=mip_data)
