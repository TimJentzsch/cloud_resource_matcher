"""Implementation of the validation step for the service limits module."""
from optiframe import ValidationTask

from cloud_resource_matcher.modules.base import BaseData

from .data import ServiceLimitsData


class ValidationServiceLimitsTask(ValidationTask):
    """A task to validate the data for the service limits module."""

    base_data: BaseData
    service_limits_data: ServiceLimitsData

    def __init__(self, base_data: BaseData, service_limits_data: ServiceLimitsData):
        self.base_data = base_data
        self.service_limits_data = service_limits_data

    def validate(self) -> None:
        """Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate cs_to_instance_limit
        for (cs, instances) in self.service_limits_data.cs_to_instance_limit.items():
            assert (
                cs in self.base_data.cloud_services
            ), f"{cs} in cs_to_instance_limit is not a valid CS"
            assert instances >= 0, f"Negative max instance count {instances} for CS {cs}"

        # Validate cr_to_max_instance_demand
        for cr, max_instance_demand in self.service_limits_data.cr_to_max_instance_demand.items():
            assert (
                cr in self.base_data.cloud_resources
            ), f"{cr} in cr_to_max_instance_demand is not a valid CR"
            assert (
                max_instance_demand >= 0
            ), f"Negative max instance demand {max_instance_demand} for CR {cr}"

            total_instance_demand = self.base_data.cr_to_instance_demand[cr]

            assert max_instance_demand <= total_instance_demand, (
                f"The maximum instance demand {max_instance_demand} for CR {cr}"
                f" cannot be larger than the total instance demand {total_instance_demand}"
            )

        for cr in self.base_data.cloud_resources:
            assert (
                cr in self.service_limits_data.cr_to_max_instance_demand.keys()
            ), f"CR {cr} does not have a maximum instance demand specified"
