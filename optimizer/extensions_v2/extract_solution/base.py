from dataclasses import dataclass

from pulp import pulp

from optimizer.data import BaseData
from optimizer.data.types import VirtualMachine, Service, TimeUnit
from optimizer.extensions_v2.build_mip.base import BaseMipData
from optimizer.optimizer_v2.extension import Extension


VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]


@dataclass
class BaseSolution:
    """
    The most important parts of the solution, including the assignment
    of VMs to services and the number of service instances to buy.
    """

    # Which VM should be deployed on which service?
    vm_service_matching: VmServiceMatching
    # How many instances of each service should be bought?
    service_instance_count: ServiceInstanceCount


class ExtractSolutionBaseExt(Extension[BaseSolution]):
    base_data: BaseData
    base_mip_data: BaseMipData

    def __init__(self, base_data: BaseData, base_mip_data: BaseMipData):
        self.base_data = base_data
        self.base_mip_data = base_mip_data

    def action(self) -> BaseSolution:
        vm_service_matching: VmServiceMatching = dict()

        for v in self.base_data.virtual_machines:
            for s in self.base_data.virtual_machine_services[v]:
                for t in self.base_data.time:
                    value = (
                        round(pulp.value(self.base_mip_data.var_vm_matching[v, s]))
                        * self.base_data.virtual_machine_demand[v, t]
                    )

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in self.base_data.services:
            for t in self.base_data.time:
                value = sum(
                    round(pulp.value(self.base_mip_data.var_vm_matching[vm, s]))
                    * self.base_data.virtual_machine_demand[vm, t]
                    for vm in self.base_data.virtual_machines
                    if s in self.base_data.virtual_machine_services[vm]
                )

                if value >= 1:
                    service_instance_count[s, t] = value

        return BaseSolution(
            vm_service_matching=vm_service_matching,
            service_instance_count=service_instance_count,
        )
