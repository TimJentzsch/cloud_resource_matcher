from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpVariable, LpBinary, lpSum

from .base import BaseMipData
from .extension import Extension, ExtensionId
from optimizer.optimizer_toolbox_model import BaseData
from optimizer.extensions.decorators import dependencies
from optimizer.optimizer_toolbox_model import NetworkData
from optimizer.optimizer_toolbox_model.data import VirtualMachine
from optimizer.optimizer_toolbox_model.data.network_data import Location


@dataclass
class NetworkMipData:
    data: NetworkData
    var_vm_locations: dict[tuple[VirtualMachine, Location], LpVariable]
    var_vm_vm_locations: dict[
        tuple[VirtualMachine, VirtualMachine, Location, Location],
        LpVariable,
    ]


@dataclass
class NetworkSolutionData:
    mip_data: NetworkMipData


class NetworkExtension(Extension):
    @staticmethod
    def identifier() -> ExtensionId:
        return "network"

    @staticmethod
    @dependencies("base")
    def validate(data: NetworkData, base: BaseData):
        data.validate(base)

    @staticmethod
    @dependencies("base")
    def extend_mip(
        data: NetworkData,
        problem: LpProblem,
        objective: LpAffineExpression,
        base: BaseMipData,
    ) -> NetworkMipData:
        # Are the VMs v located at location loc?
        var_vm_locations: dict[tuple[VirtualMachine, Location], LpVariable] = {
            (v, loc): LpVariable(
                f"vm_location({v},{loc})",
                cat=LpBinary,
            )
            for v in base.data.virtual_machines
            for loc in data.locations
        }

        # All VMs are placed at exactly one location
        for v in base.data.virtual_machines:
            problem += (
                lpSum(var_vm_locations[v, loc] for loc in data.locations) == 1,
                f"one_vm_location({v})",
            )

        # The VMs location is the location of the service where it's placed
        for v in base.data.virtual_machines:
            for loc in data.locations:
                for s in base.data.virtual_machine_services[v]:
                    if loc in data.service_location[s]:
                        problem += (
                            var_vm_locations[v, loc] >= base.var_vm_matching[v, s]
                        )

        # Pay for VM -> location traffic
        objective += lpSum(
            var_vm_locations[vm, vm_loc]
            * base.data.virtual_machine_demand[vm, t]
            * traffic
            * data.location_traffic_cost[vm_loc, loc]
            for (
                vm,
                loc,
            ), traffic in data.virtual_machine_location_traffic.items()
            for vm_loc in data.locations
            for t in base.data.time
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
            ) in data.virtual_machine_virtual_machine_traffic.keys()
            for loc1 in data.locations
            for loc2 in data.locations
        }

        # The connections must be at the locations where the VMs are actually placed
        for (
            vm1,
            vm2,
        ) in data.virtual_machine_virtual_machine_traffic.keys():
            # Make enough outgoing connections from each location
            for loc1 in data.locations:
                problem += var_vm_locations[vm1, loc1] == lpSum(
                    var_vm_vm_locations[vm1, vm2, loc1, loc2] for loc2 in data.locations
                )

            # Have at least one VM at the incoming location
            for loc1 in data.locations:
                for loc2 in data.locations:
                    problem += (
                        var_vm_locations[vm2, loc2]
                        >= var_vm_vm_locations[vm1, vm2, loc1, loc2]
                    )

        # Respect maximum latencies for VM -> location traffic
        for (
            vm1,
            loc2,
        ), max_latency in data.virtual_machine_location_max_latency.items():
            for loc1 in data.locations:
                if data.location_latency[loc1, loc2] > max_latency:
                    if (
                        vm1,
                        loc2,
                    ) in data.virtual_machine_location_traffic.keys():
                        problem += var_vm_locations[vm1, loc1] == 0

        # Respect maximum latencies for VM -> VM traffic
        for (
            vm1,
            vm2,
        ), max_latency in data.virtual_machine_virtual_machine_max_latency.items():
            for loc1 in data.locations:
                for loc2 in data.locations:
                    if data.location_latency[loc1, loc2] > max_latency:
                        problem += var_vm_vm_locations[vm1, vm2, loc1, loc2] == 0

        # Pay for VM -> location traffic caused by VM -> VM connections
        objective += lpSum(
            var_vm_vm_locations[vm1, vm2, loc1, loc2]
            * base.data.virtual_machine_demand[vm1, t]
            * traffic
            * data.location_traffic_cost[loc1, loc2]
            for (
                vm1,
                vm2,
            ), traffic in data.virtual_machine_virtual_machine_traffic.items()
            for loc1 in data.locations
            for loc2 in data.locations
            for t in base.data.time
        )

        return NetworkMipData(
            data=data,
            var_vm_locations=var_vm_locations,
            var_vm_vm_locations=var_vm_vm_locations,
        )

    @staticmethod
    @dependencies()
    def extract_solution(mip_data: NetworkMipData, problem: LpProblem) -> NetworkSolutionData:
        # TODO: Extract location data
        return NetworkSolutionData(mip_data=mip_data)
