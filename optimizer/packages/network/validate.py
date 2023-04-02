from optiframe import Task

from optimizer.packages.base import BaseData
from .data import NetworkData


class ValidateNetworkTask(Task[None]):
    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def execute(self) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate location_latency
        for (loc1, loc2), latency in self.network_data.location_latency.items():
            assert (
                loc1 in self.network_data.locations
            ), f"{loc1} in location_latency is not a valid location"
            assert (
                loc2 in self.network_data.locations
            ), f"{loc2} in location_latency is not a valid location"

            assert latency >= 0, "Latency must not be negative"

        for loc1 in self.network_data.locations:
            for loc2 in self.network_data.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.network_data.location_latency.keys(), (
                    f"No definition for location latency between {loc1} and {loc2}"
                )

        # Validate service_location
        for s, loc in self.network_data.service_location.items():
            assert s in self.base_data.services, f"{s} in service_location is not a valid service"
            assert (
                loc in self.network_data.locations
            ), f"{loc} in service_location is not a valid location"

        for s in self.base_data.services:
            assert (
                s in self.network_data.service_location.keys()
            ), f"No location defined for service {s}"

        # Validate virtual_machine_max_latency
        for (v, loc), latency in self.network_data.virtual_machine_location_max_latency.items():
            assert (
                v in self.base_data.virtual_machines
            ), f"{v} in virtual_machine_max_latency is not a valid VM"
            assert (
                loc in self.network_data.locations
            ), f"{loc} in virtual_machine_max_latency is not a valid location"

            assert latency >= 0, "The maximum latency must not be negative"

        # Validate virtual_machine_location_traffic
        for (v, loc), traffic in self.network_data.virtual_machine_location_traffic.items():
            assert (
                v in self.base_data.virtual_machines
            ), f"{v} in virtual_machine_location_traffic is not a valid VM"
            assert (
                loc in self.network_data.locations
            ), f"{loc} in virtual_machine_location_traffic is not a valid location"

            assert traffic >= 0, f"Traffic for VM {v} and location {loc} must not be negative"

        # Validate virtual_machine_virtual_machine_traffic
        for (v1, v2), traffic in self.network_data.virtual_machine_virtual_machine_traffic.items():
            assert (
                v1 in self.base_data.virtual_machines
            ), f"{v1} in virtual_machine_virtual_machine_traffic is not a valid VM"
            assert (
                v2 in self.base_data.virtual_machines
            ), f"{v2} in virtual_machine_virtual_machine_traffic is not a valid VM"

            assert traffic >= 0, f"Traffic for VM {v1} and VM {v2} must not be negative"

        # Validate location_traffic_cost
        for loc1, loc2 in self.network_data.location_traffic_cost:
            assert (
                loc1 in self.network_data.locations
            ), f"{loc1} in location_traffic_cost is not a valid location"
            assert (
                loc2 in self.network_data.locations
            ), f"{loc2} in location_traffic_cost is not a valid location"

        for loc1 in self.network_data.locations:
            for loc2 in self.network_data.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.network_data.location_traffic_cost.keys(), (
                    f"No network traffic costs specified for ({loc1}, {loc2})"
                )
