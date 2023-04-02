from optiframe import Task

from optimizer.packages.base import BaseData
from .data import MultiCloudData


class ValidateMultiCloudTask(Task[None]):
    base_data: BaseData
    multi_cloud_data: MultiCloudData

    def __init__(self, base_data: BaseData, multi_cloud_data: MultiCloudData):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data

    def execute(self) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate cloud_service_provider_services
        for csp in self.multi_cloud_data.cloud_service_providers:
            assert (
                csp in self.multi_cloud_data.cloud_service_provider_services.keys()
            ), f"CSP {csp} is missing in cloud_service_provider_services"

        for csp, services in self.multi_cloud_data.cloud_service_provider_services.items():
            assert (
                csp in self.multi_cloud_data.cloud_service_providers
            ), f"{csp} in cloud_service_provider_services is not a valid CSP"

            for s in services:
                assert (
                    s in self.base_data.services
                ), f"{s} in cloud_service_provider_services is not a valid service"

        for s in self.base_data.services:
            matched_to_csp = False

            for services in self.multi_cloud_data.cloud_service_provider_services.values():
                if s in services:
                    matched_to_csp = True
                    break

            assert matched_to_csp is True

        # Validate min/max counts
        assert (
            self.multi_cloud_data.min_cloud_service_provider_count >= 0
        ), "min_cloud_service_provider_count is negative"
        assert (
            self.multi_cloud_data.max_cloud_service_provider_count >= 0
        ), "max_cloud_service_provider_count is negative"
        assert (
            self.multi_cloud_data.min_cloud_service_provider_count
            <= self.multi_cloud_data.max_cloud_service_provider_count
        ), (
            "min_cloud_service_provider_count must be smaller or equal"
            "than max_cloud_service_provider_count"
        )

        # Validate costs
        for csp in self.multi_cloud_data.cloud_service_providers:
            assert (
                csp in self.multi_cloud_data.cloud_service_provider_costs
            ), f"CSP {csp} does not have a cost defined"
