"""Implementation of the validation step for the base module."""
from optiframe import ValidationTask

from .data import BaseData


class ValidationBaseTask(ValidationTask):
    """A task to validate the data of the base module."""

    base_data: BaseData

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def validate(self) -> None:
        """Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate cr_to_cs_list
        for cr in self.base_data.cloud_resources:
            assert cr in self.base_data.cr_to_cs_list.keys(), f"Valid CSs for CR {cr} not defined"

        for cr, services in self.base_data.cr_to_cs_list.items():
            assert cr in self.base_data.cloud_resources, f"{cr} in cr_to_cs_list is not a valid CR"
            for cs in services:
                assert (
                    cs in self.base_data.cloud_services
                ), f"{cs} in cr_to_cs_list is not a valid CS"

        # Validate cs_to_base_cost
        for cs in self.base_data.cloud_services:
            assert cs in self.base_data.cs_to_base_cost.keys(), f"Base cost for CS {cs} not defined"

        for cs, cost in self.base_data.cs_to_base_cost.items():
            assert cs in self.base_data.cloud_services, f"{cs} in cs_to_base_cost is not a valid CS"
            assert cost >= 0, f"Cost {cost} for CS {cs} is negative"

        # Validate cr_to_instance_demand
        for cr, demand in self.base_data.cr_to_instance_demand.items():
            assert (
                cr in self.base_data.cloud_resources
            ), f"{cr} in cr_and_time_to_instance_demand is not a valid CR"
            assert demand >= 0, f"Demand {demand} for CR {cr} is negative"

        for cr in self.base_data.cloud_resources:
            assert (
                cr in self.base_data.cr_to_instance_demand.keys()
            ), f"No demand defined for CR {cr}"
