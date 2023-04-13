from dataclasses import dataclass

from optiframe.framework.tasks import ExtractSolutionTask
from pulp import pulp

from .data import BaseData, CloudService, CloudResource
from .build_mip import BaseMipData

CrToCsMatching = dict[tuple[CloudResource, CloudService], int]
ServiceInstanceCount = dict[CloudService, int]


@dataclass
class BaseSolution:
    """
    The most important parts of the solution, including the assignment
    of CRs to CSs and the number of CS instances to buy.
    """

    # Which cloud resource should be deployed on which cloud service?
    cr_to_cs_matching: CrToCsMatching
    # How many instances of each service should be bought?
    cs_instance_count: ServiceInstanceCount


class ExtractSolutionBaseTask(ExtractSolutionTask[BaseSolution]):
    base_data: BaseData
    base_mip_data: BaseMipData

    def __init__(self, base_data: BaseData, base_mip_data: BaseMipData):
        self.base_data = base_data
        self.base_mip_data = base_mip_data

    def execute(self) -> BaseSolution:
        cr_to_cs_matching: CrToCsMatching = dict()

        for cr in self.base_data.cloud_resources:
            for cs in self.base_data.cr_to_cs_list[cr]:
                value = (
                    round(pulp.value(self.base_mip_data.var_cr_to_cs_matching[cr, cs]))
                    * self.base_data.cr_and_time_to_instance_demand[cr]
                )

                if value >= 1:
                    cr_to_cs_matching[cr, cs] = value

        cs_instance_count: ServiceInstanceCount = {}

        for cs in self.base_data.cloud_services:
            value = sum(
                round(pulp.value(self.base_mip_data.var_cr_to_cs_matching[cr, cs]))
                * self.base_data.cr_and_time_to_instance_demand[cr]
                for cr in self.base_data.cloud_resources
                if cs in self.base_data.cr_to_cs_list[cr]
            )

            if value >= 1:
                cs_instance_count[cs] = value

        return BaseSolution(
            cr_to_cs_matching=cr_to_cs_matching,
            cs_instance_count=cs_instance_count,
        )
