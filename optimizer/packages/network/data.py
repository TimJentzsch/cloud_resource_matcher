from dataclasses import dataclass

from optimizer.packages.base.data import Service, VirtualMachine

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

    # The network traffic between a virtual machine and a given location
    virtual_machine_location_traffic: dict[tuple[VirtualMachine, Location], NetworkTraffic]

    # The maximum latency a virtual machine can have to a given location
    # There must be traffic between the VM and the location
    virtual_machine_location_max_latency: dict[tuple[VirtualMachine, Location], Latency]

    # The network traffic between two virtual machines
    virtual_machine_virtual_machine_traffic: dict[
        tuple[VirtualMachine, VirtualMachine], NetworkTraffic
    ]

    # The maximum latency between two virtual machines
    # There must be traffic between the two virtual machines
    virtual_machine_virtual_machine_max_latency: dict[
        tuple[VirtualMachine, VirtualMachine], Latency
    ]

    # The cost of network traffic between two locations
    # This must be specified for every pair of locations
    location_traffic_cost: dict[tuple[Location, Location], float]
