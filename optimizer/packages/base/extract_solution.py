from dataclasses import dataclass

from pulp import pulp

from .data import BaseData, CloudService, CloudResource, TimeUnit
from .build_mip import BaseMipData
from optiframe import Task

VmServiceMatching = dict[tuple[CloudResource, CloudService, TimeUnit], int]
ServiceInstanceCount = dict[tuple[CloudService, TimeUnit], int]


@dataclass
class BaseSolution:
    """
    The most important parts of the solution, including the assignment
    of VMs to cloud_services and the number of service instances to buy.
    """

    # Which VM should be deployed on which service?
    vm_service_matching: VmServiceMatching
    # How many instances of each service should be bought?
    service_instance_count: ServiceInstanceCount


class ExtractSolutionBaseTask(Task[BaseSolution]):
    base_data: BaseData
    base_mip_data: BaseMipData

    def __init__(self, base_data: BaseData, base_mip_data: BaseMipData):
        self.base_data = base_data
        self.base_mip_data = base_mip_data

    def execute(self) -> BaseSolution:
        vm_service_matching: VmServiceMatching = dict()

        for v in self.base_data.cloud_resources:
            for s in self.base_data.cr_to_cs_list[v]:
                for t in self.base_data.time:
                    value = (
                        round(pulp.value(self.base_mip_data.var_cr_to_cs_matching[v, s]))
                        * self.base_data.cr_and_time_to_instance_demand[v, t]
                    )

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in self.base_data.cloud_services:
            for t in self.base_data.time:
                value = sum(
                    round(pulp.value(self.base_mip_data.var_cr_to_cs_matching[vm, s]))
                    * self.base_data.cr_and_time_to_instance_demand[vm, t]
                    for vm in self.base_data.cloud_resources
                    if s in self.base_data.cr_to_cs_list[vm]
                )

                if value >= 1:
                    service_instance_count[s, t] = value

        return BaseSolution(
            vm_service_matching=vm_service_matching,
            service_instance_count=service_instance_count,
        )
