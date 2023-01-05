from dataclasses import dataclass

from optimizer.data import VirtualMachine, Service

Location = str
Latency = int
NetworkTraffic = int


@dataclass
class NetworkData:
    # A locations that affect latency and network prices
    # Can be physical or virtual locations
    locations: set[Location]

    # The latency between two locations
    location_latency: dict[tuple[Location, Location], Latency]

    # The location that a service is placed in
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
    location_traffic_cost: dict[tuple[Location, Location], float]
