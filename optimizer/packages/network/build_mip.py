from dataclasses import dataclass

from pulp import LpProblem, LpBinary, LpVariable, lpSum

from optimizer.data import BaseData, NetworkData
from optimizer.data.types import VirtualMachine, Service
from optimizer.packages.base import BaseMipData
from optiframe import Task


@dataclass
class NetworkMipData:
    # Is vm1 deployed to s1 and vm2 deployed to s2?
    var_vm_pair_services: dict[tuple[VirtualMachine, Service, VirtualMachine, Service], LpVariable]


class BuildMipNetworkTask(Task[NetworkMipData]):
    base_data: BaseData
    network_data: NetworkData
    base_mip_data: BaseMipData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        network_data: NetworkData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.network_data = network_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def execute(self) -> NetworkMipData:
        # Pay for VM -> location traffic
        self.problem.objective += lpSum(
            self.base_mip_data.var_vm_matching[vm, s]
            * self.base_data.virtual_machine_demand[vm, t]
            * traffic
            * self.network_data.location_traffic_cost[self.network_data.service_location[s], loc]
            for (
                vm,
                loc,
            ), traffic in self.network_data.virtual_machine_location_traffic.items()
            for s in self.base_data.virtual_machine_services[vm]
            for t in self.base_data.time
        )

        # === virtual_machine_virtual_machine_traffic ===

        # Is there a vm1 -> vm2 connection where vm1 is deployed to s1 and vm2 to s2?
        var_vm_pair_services: dict[
            tuple[VirtualMachine, Service, VirtualMachine, Service],
            LpVariable,
        ] = {
            (vm1, s1, vm2, s2): LpVariable(
                f"vm_pair_services({vm1},{s1},{vm2},{s2})",
                cat=LpBinary,
            )
            for (
                vm1,
                vm2,
            ) in self.network_data.virtual_machine_virtual_machine_traffic.keys()
            for s1 in self.base_data.virtual_machine_services[vm1]
            for s2 in self.base_data.virtual_machine_services[vm2]
        }

        # Calculate service pair deployments
        for (
            vm1,
            vm2,
        ) in self.network_data.virtual_machine_virtual_machine_traffic.keys():
            # Every VM pair has one pair of service connections
            self.problem += (
                lpSum(
                    var_vm_pair_services[vm1, s1, vm2, s2]
                    for s1 in self.base_data.virtual_machine_services[vm1]
                    for s2 in self.base_data.virtual_machine_services[vm2]
                )
                == 1
            )

            # Enforce that the VMs must be deployed to the given services
            for s1 in self.base_data.virtual_machine_services[vm1]:
                for s2 in self.base_data.virtual_machine_services[vm2]:
                    self.problem += (
                        var_vm_pair_services[vm1, s1, vm2, s2]
                        <= self.base_mip_data.var_vm_matching[vm1, s1]
                    )
                    self.problem += (
                        var_vm_pair_services[vm1, s1, vm2, s2]
                        <= self.base_mip_data.var_vm_matching[vm2, s2]
                    )

        # Respect maximum latencies for VM -> location traffic
        for (
            vm1,
            loc2,
        ), max_latency in self.network_data.virtual_machine_location_max_latency.items():
            for s in self.base_data.virtual_machine_services[vm1]:
                loc1 = self.network_data.service_location[s]

                if self.network_data.location_latency[loc1, loc2] > max_latency:
                    if (
                        vm1,
                        loc2,
                    ) in self.network_data.virtual_machine_location_traffic.keys():
                        self.problem += self.base_mip_data.var_vm_matching[vm1, s] == 0

        # Respect maximum latencies for VM -> VM traffic
        for (
            vm1,
            vm2,
        ), max_latency in self.network_data.virtual_machine_virtual_machine_max_latency.items():
            for s1 in self.base_data.virtual_machine_services[vm1]:
                loc1 = self.network_data.service_location[s1]

                for s2 in self.base_data.virtual_machine_services[vm2]:
                    loc2 = self.network_data.service_location[s2]

                    if self.network_data.location_latency[loc1, loc2] > max_latency:
                        self.problem += var_vm_pair_services[vm1, s1, vm2, s2] == 0

        # Pay for VM -> location traffic caused by VM -> VM connections
        self.problem.objective += lpSum(
            var_vm_pair_services[vm1, s1, vm2, s2]
            * self.base_data.virtual_machine_demand[vm1, t]
            * traffic
            * self.network_data.location_traffic_cost[
                self.network_data.service_location[s1], self.network_data.service_location[s2]
            ]
            for (
                vm1,
                vm2,
            ), traffic in self.network_data.virtual_machine_virtual_machine_traffic.items()
            for s1 in self.base_data.virtual_machine_services[vm1]
            for s2 in self.base_data.virtual_machine_services[vm2]
            for t in self.base_data.time
        )

        return NetworkMipData(var_vm_pair_services)
