"""Implementation of the validation step for the network module."""
from optiframe import ValidationTask

from cloud_resource_matcher.modules.base import BaseData

from .data import NetworkData


class ValidateNetworkTask(ValidationTask):
    """Validate the data provided for the network module."""

    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def validate(self) -> None:
        """Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate loc_and_loc_to_latency
        for (loc1, loc2), latency in self.network_data.loc_and_loc_to_latency.items():
            assert (
                loc1 in self.network_data.locations
            ), f"{loc1} in loc_and_loc_to_latency is not a valid location"
            assert (
                loc2 in self.network_data.locations
            ), f"{loc2} in loc_and_loc_to_latency is not a valid location"

            assert latency >= 0, "Latency must not be negative"

        for loc1 in self.network_data.locations:
            for loc2 in self.network_data.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.network_data.loc_and_loc_to_latency.keys(), (
                    f"No definition for location latency between {loc1} and {loc2}"
                )

        # Validate cs_to_loc
        for cs, loc in self.network_data.cs_to_loc.items():
            assert cs in self.base_data.cloud_services, f"{cs} in cs_to_loc is not a valid service"
            assert loc in self.network_data.locations, f"{loc} in cs_to_loc is not a valid location"

        for cs in self.base_data.cloud_services:
            assert cs in self.network_data.cs_to_loc.keys(), f"No location defined for service {cs}"

        # Validate cr_and_loc_to_max_latency
        for (cr, loc), latency in self.network_data.cr_and_loc_to_max_latency.items():
            assert (
                cr in self.base_data.cloud_resources
            ), f"{cr} in cr_and_loc_to_max_latency is not a valid VM"
            assert (
                loc in self.network_data.locations
            ), f"{loc} in cr_and_loc_to_max_latency is not a valid location"

            assert latency >= 0, "The maximum latency must not be negative"

        # Validate cr_and_loc_to_traffic
        for (cr, loc), traffic in self.network_data.cr_and_loc_to_traffic.items():
            assert (
                cr in self.base_data.cloud_resources
            ), f"{cr} in cr_and_loc_to_traffic is not a valid CR"
            assert (
                loc in self.network_data.locations
            ), f"{loc} in cr_and_loc_to_traffic is not a valid location"

            assert traffic >= 0, f"Traffic from CR {cr} to location {loc} must not be negative"

        # Validate cr_and_cr_to_traffic
        for (cr1, cr2), traffic in self.network_data.cr_and_cr_to_traffic.items():
            assert (
                cr1 in self.base_data.cloud_resources
            ), f"{cr1} in cr_and_cr_to_traffic is not a valid CR"
            assert (
                cr2 in self.base_data.cloud_resources
            ), f"{cr2} in cr_and_cr_to_traffic is not a valid CR"

            assert traffic >= 0, f"Traffic from CR {cr1} to CR {cr2} must not be negative"

        # Validate loc_and_loc_to_cost
        for loc1, loc2 in self.network_data.loc_and_loc_to_cost:
            assert (
                loc1 in self.network_data.locations
            ), f"{loc1} in loc_and_loc_to_cost is not a valid location"
            assert (
                loc2 in self.network_data.locations
            ), f"{loc2} in loc_and_loc_to_cost is not a valid location"

        for loc1 in self.network_data.locations:
            for loc2 in self.network_data.locations:
                assert (
                    loc1,
                    loc2,
                ) in self.network_data.loc_and_loc_to_cost.keys(), (
                    f"No network traffic costs specified for ({loc1}, {loc2})"
                )
