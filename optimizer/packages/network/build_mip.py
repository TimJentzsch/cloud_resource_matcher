from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpBinary, LpVariable, lpSum

from optimizer.data import BaseData, NetworkData
from optimizer.data.network import Location
from optimizer.data.types import VirtualMachine
from optimizer.packages.base import BaseMipData
from optimizer.workflow_engine import Task


@dataclass
class NetworkMipData:
    var_vm_locations: dict[tuple[VirtualMachine, Location], LpVariable]
    var_vm_vm_locations: dict[
        tuple[VirtualMachine, VirtualMachine, Location, Location],
        LpVariable,
    ]


class BuildMipNetworkTask(Task[NetworkMipData]):
    base_data: BaseData
    network_data: NetworkData
    base_mip_data: BaseMipData
    problem: LpProblem
    objective: LpAffineExpression

    def __init__(
        self,
        base_data: BaseData,
        network_data: NetworkData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
        objective: LpAffineExpression,
    ):
        self.base_data = base_data
        self.network_data = network_data
        self.base_mip_data = base_mip_data
        self.problem = problem
        self.objective = objective

    def execute(self) -> NetworkMipData:
        # Are the VMs v located at location loc?
        var_vm_locations: dict[tuple[VirtualMachine, Location], LpVariable] = {
            (v, loc): LpVariable(
                f"vm_location({v},{loc})",
                cat=LpBinary,
            )
            for v in self.base_data.virtual_machines
            for loc in self.network_data.locations
        }

        # All VMs are placed at exactly one location
        for v in self.base_data.virtual_machines:
            self.problem += (
                lpSum(var_vm_locations[v, loc] for loc in self.network_data.locations) == 1,
                f"one_vm_location({v})",
            )

        # The VMs location is the location of the service where it's placed
        for v in self.base_data.virtual_machines:
            for s in self.base_data.virtual_machine_services[v]:
                loc = self.network_data.service_location[s]
                self.problem += var_vm_locations[v, loc] >= self.base_mip_data.var_vm_matching[v, s]

        # Pay for VM -> location traffic
        self.objective += lpSum(
            var_vm_locations[vm, vm_loc]
            * self.base_data.virtual_machine_demand[vm, t]
            * traffic
            * self.network_data.location_traffic_cost[vm_loc, loc]
            for (
                vm,
                loc,
            ), traffic in self.network_data.virtual_machine_location_traffic.items()
            for vm_loc in self.network_data.locations
            for t in self.base_data.time
        )

        # === virtual_machine_virtual_machine_traffic ===

        # Is there a vm1 -> vm2 connection where vm1 is at loc1
        # and vm2 is at loc2
        var_vm_vm_locations: dict[
            tuple[VirtualMachine, VirtualMachine, Location, Location],
            LpVariable,
        ] = {
            (vm1, vm2, loc1, loc2): LpVariable(
                f"vm_vm_locations({vm1},{vm2},{loc1},{loc2})",
                cat=LpBinary,
            )
            for (
                vm1,
                vm2,
            ) in self.network_data.virtual_machine_virtual_machine_traffic.keys()
            for loc1 in self.network_data.locations
            for loc2 in self.network_data.locations
        }

        # The connections must be at the locations where the VMs are actually placed
        for (
            vm1,
            vm2,
        ) in self.network_data.virtual_machine_virtual_machine_traffic.keys():
            # Make enough outgoing connections from each location
            for loc1 in self.network_data.locations:
                self.problem += var_vm_locations[vm1, loc1] == lpSum(
                    var_vm_vm_locations[vm1, vm2, loc1, loc2]
                    for loc2 in self.network_data.locations
                )

            # Have at least one VM at the incoming location
            for loc1 in self.network_data.locations:
                for loc2 in self.network_data.locations:
                    self.problem += (
                        var_vm_locations[vm2, loc2] >= var_vm_vm_locations[vm1, vm2, loc1, loc2]
                    )

        # Respect maximum latencies for VM -> location traffic
        for (
            vm1,
            loc2,
        ), max_latency in self.network_data.virtual_machine_location_max_latency.items():
            for loc1 in self.network_data.locations:
                if self.network_data.location_latency[loc1, loc2] > max_latency:
                    if (
                        vm1,
                        loc2,
                    ) in self.network_data.virtual_machine_location_traffic.keys():
                        self.problem += var_vm_locations[vm1, loc1] == 0

        # Respect maximum latencies for VM -> VM traffic
        for (
            vm1,
            vm2,
        ), max_latency in self.network_data.virtual_machine_virtual_machine_max_latency.items():
            for loc1 in self.network_data.locations:
                for loc2 in self.network_data.locations:
                    if self.network_data.location_latency[loc1, loc2] > max_latency:
                        self.problem += var_vm_vm_locations[vm1, vm2, loc1, loc2] == 0

        # Pay for VM -> location traffic caused by VM -> VM connections
        self.objective += lpSum(
            var_vm_vm_locations[vm1, vm2, loc1, loc2]
            * self.base_data.virtual_machine_demand[vm1, t]
            * traffic
            * self.network_data.location_traffic_cost[loc1, loc2]
            for (
                vm1,
                vm2,
            ), traffic in self.network_data.virtual_machine_virtual_machine_traffic.items()
            for loc1 in self.network_data.locations
            for loc2 in self.network_data.locations
            for t in self.base_data.time
        )

        return NetworkMipData(var_vm_locations, var_vm_vm_locations)
