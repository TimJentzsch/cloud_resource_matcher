from dataclasses import dataclass
from typing import Self

from optimizer.data import VirtualMachine, Service
from optimizer.data.base_data import BaseData
from optimizer.data.validated import Validated

Location = str
Latency = int
NetworkTraffic = int


@dataclass
class NetworkData:
    # A locations that affect latency and network prices
    # Can be physical or virtual locations
    locations: set[Location]

    # The latency between two locations
    # This must be specified for every pair of locations
    location_latency: dict[tuple[Location, Location], Latency]

    # The location that a service is placed in
    # This must be specified for every service
    service_location: dict[Service, Location]

    # The maximum latency a virtual machine can have to a given location
    virtual_machine_max_latency: dict[tuple[VirtualMachine, Location], Latency]

    # The network traffic between a virtual machine and a given location
    virtual_machine_location_traffic: dict[
        tuple[VirtualMachine, Location], NetworkTraffic
    ]

    # The network traffic between two virtual machines
    virtual_machine_virtual_machine_traffic: dict[
        tuple[VirtualMachine, VirtualMachine], NetworkTraffic
    ]

    # The cost of network traffic between two locations
    # This must be specified for every pair of locations
    location_traffic_cost: dict[tuple[Location, Location], float]

    def validate(self, base_data: BaseData) -> Validated[Self]:
        # Validate location_latency
        for loc1, loc2 in self.location_latency.keys():
            assert (
                loc1 in self.locations
            ), f"{loc1} in location_latency is not a valid location"
            assert (
                loc2 in self.locations
            ), f"{loc2} in location_latency is not a valid location"

        for loc1 in self.locations:
            for loc2 in self.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.location_latency.keys(), (
                    f"No definition for location latency between {loc1} and {loc2}"
                )

        # Validate service_location
        for s, loc in self.service_location.items():
            assert (
                s in base_data.services
            ), f"{s} in service_location is not a valid service"
            assert (
                loc in self.locations
            ), f"{loc} in service_location is not a valid location"

        for s in base_data.services:
            assert (
                s in self.service_location.keys()
            ), f"No location defined for service {s}"

        # Validate virtual_machine_max_latency
        for v, loc in self.virtual_machine_max_latency.keys():
            assert (
                v in base_data.virtual_machines
            ), f"{v} in virtual_machine_max_latency is not a valid VM"
            assert (
                loc in self.locations
            ), f"{loc} in virtual_machine_max_latency is not a valid location"

        # Validate virtual_machine_location_traffic
        for v, loc in self.virtual_machine_location_traffic.keys():
            assert (
                v in base_data.virtual_machines
            ), f"{v} in virtual_machine_location_traffic is not a valid VM"
            assert (
                loc in self.locations
            ), f"{loc} in virtual_machine_location_traffic is not a valid location"

        # Validate virtual_machine_virtual_machine_traffic
        for v1, v2 in self.virtual_machine_virtual_machine_traffic.keys():
            assert (
                v1 in base_data.virtual_machines
            ), f"{v1} in virtual_machine_virtual_machine_traffic is not a valid VM"
            assert (
                v2 in base_data.virtual_machines
            ), f"{v2} in virtual_machine_virtual_machine_traffic is not a valid VM"

        # Validate location_traffic_cost
        for loc1, loc2 in self.location_traffic_cost:
            assert (
                loc1 in self.locations
            ), f"{loc1} in location_traffic_cost is not a valid location"
            assert (
                loc2 in self.locations
            ), f"{loc2} in location_traffic_cost is not a valid location"

        for loc1 in self.locations:
            for loc2 in self.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.location_traffic_cost.keys(), (
                    f"No network traffic costs specified for ({loc1}, {loc2})"
                )

        return Validated(self)
