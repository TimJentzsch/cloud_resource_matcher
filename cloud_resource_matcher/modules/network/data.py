"""The data for the network module."""
from dataclasses import dataclass

from cloud_resource_matcher.modules.base.data import CloudResource, CloudService, Cost

Location = str
Latency = int
NetworkTraffic = int


@dataclass
class NetworkData:
    """The data for the network module.

    Can be used to specify the available network locations,
    connections between CRs and locations or pairs of CRs
    and used to enforce maximum latency requirements.
    Costs for network traffic can also be specified.
    """

    # A locations that affect latency and network prices.
    # Can be physical or virtual locations.
    locations: set[Location]

    # A map from a loc -> loc connection to the latency that is expected for that connection.
    # This must be defined for every pair of locations.
    loc_and_loc_to_latency: dict[tuple[Location, Location], Latency]

    # A map from a cloud service to the location it is placed in.
    cs_to_loc: dict[CloudService, Location]

    # A map from a CR -> loc connection to the network traffic of that connection.
    # The traffic is given per CR instance and per unit of time.
    cr_and_loc_to_traffic: dict[tuple[CloudResource, Location], NetworkTraffic]

    # A map from a CR -> loc connection to the maximum latency allowed on that connection.
    # This can be used to enforce a maximum latency to end users in a given region.
    cr_and_loc_to_max_latency: dict[tuple[CloudResource, Location], Latency]

    # A map from a CR -> CR connection to the network traffic of that connection.
    # The traffic is given per (starting) CR instance and per unit of time.
    cr_and_cr_to_traffic: dict[tuple[CloudResource, CloudResource], NetworkTraffic]

    # A map from a CR -> CR connection to the maximum latency allowed on that connection.
    cr_and_cr_to_max_latency: dict[tuple[CloudResource, CloudResource], Latency]

    # A map from a loc -> loc connection to the cost of that connection.
    # The cost is given per connection, per unit of network traffic, per unit of time.
    loc_and_loc_to_cost: dict[tuple[Location, Location], Cost]
