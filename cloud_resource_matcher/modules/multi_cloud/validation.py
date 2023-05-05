"""Implementation of the validation step for the multi cloud module."""
from optiframe import ValidationTask

from cloud_resource_matcher.modules.base import BaseData

from .data import MultiCloudData


class ValidationMultiCloudTask(ValidationTask):
    """A task to validate the data for the multi cloud module."""

    base_data: BaseData
    multi_cloud_data: MultiCloudData

    def __init__(self, base_data: BaseData, multi_cloud_data: MultiCloudData):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data

    def validate(self) -> None:
        """Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate csp_to_cs_list
        for csp in self.multi_cloud_data.cloud_service_providers:
            assert (
                csp in self.multi_cloud_data.csp_to_cs_list.keys()
            ), f"CSP {csp} is missing in cloud_service_provider_services"

        for csp, services in self.multi_cloud_data.csp_to_cs_list.items():
            assert (
                csp in self.multi_cloud_data.cloud_service_providers
            ), f"{csp} in cloud_service_provider_services is not a valid CSP"

            for cs in services:
                assert (
                    cs in self.base_data.cloud_services
                ), f"{cs} in cloud_service_provider_services is not a valid service"

        for cs in self.base_data.cloud_services:
            matched_to_csp = False

            for services in self.multi_cloud_data.csp_to_cs_list.values():
                if cs in services:
                    matched_to_csp = True
                    break

            assert matched_to_csp is True

        # Validate min/max counts
        assert self.multi_cloud_data.min_csp_count >= 0, "min_csp_count is negative"
        assert self.multi_cloud_data.max_csp_count >= 0, "max_csp_count is negative"
        assert self.multi_cloud_data.min_csp_count <= self.multi_cloud_data.max_csp_count, (
            "min_csp_count must be smaller or equal" "than max_csp_count"
        )

        # Validate costs
        for csp in self.multi_cloud_data.cloud_service_providers:
            assert (
                csp in self.multi_cloud_data.csp_to_cost
            ), f"CSP {csp} does not have a cost defined"
