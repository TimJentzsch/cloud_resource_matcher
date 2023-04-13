from optiframe.framework.tasks import BuildMipTask
from pulp import LpProblem, lpSum

from optimizer.packages.base import BaseData, BaseMipData
from optimizer.packages.base.build_mip import CsToCrList
from .data import ServiceLimitsData


class BuildMipServiceLimitsTask(BuildMipTask[None]):
    base_data: BaseData
    base_mip_data: BaseMipData
    service_limits_data: ServiceLimitsData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        base_mip_data: BaseMipData,
        service_limits_data: ServiceLimitsData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.service_limits_data = service_limits_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def execute(self) -> None:
        # Pre-compute which cloud services can host which cloud resources
        cs_to_cr_list: CsToCrList = {
            cs: set(
                cr
                for cr in self.base_data.cloud_resources
                if cs in self.base_data.cr_to_cs_list[cr]
            )
            for cs in self.base_data.cloud_services
        }

        # Enforce limits for cloud service instance count
        for cs, max_instances in self.service_limits_data.cs_to_instance_limit.items():
            self.problem += (
                lpSum(
                    self.base_mip_data.var_cr_to_cs_matching[vm, cs]
                    * self.service_limits_data.cr_to_max_instance_demand[vm]
                    for vm in cs_to_cr_list[cs]
                )
                <= max_instances,
                f"cs_instance_limit({cs})",
            )
