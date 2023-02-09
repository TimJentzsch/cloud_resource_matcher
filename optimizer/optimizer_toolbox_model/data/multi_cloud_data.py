from dataclasses import dataclass
from typing import List, Dict

from optimizer.optimizer_toolbox_model.data import Service, CloudServiceProvider
from optimizer.optimizer_toolbox_model.data.base_data import BaseData


@dataclass
class MultiCloudData:
    # The available cloud service providers
    cloud_service_providers: List[CloudServiceProvider]

    # The services each cloud service provider offers
    cloud_service_provider_services: Dict[CloudServiceProvider, List[Service]]

    # The minimum number of cloud service providers that have to be used
    min_cloud_service_provider_count: int

    # The maximum number of cloud service providers that can be used
    max_cloud_service_provider_count: int

    def validate(self, base_data: BaseData) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate cloud_service_provider_services
        for csp in self.cloud_service_providers:
            assert (
                csp in self.cloud_service_provider_services.keys()
            ), f"CSP {csp} is missing in cloud_service_provider_services"

        for csp, services in self.cloud_service_provider_services.items():
            assert (
                csp in self.cloud_service_providers
            ), f"{csp} in cloud_service_provider_services is not a valid CSP"

            for s in services:
                assert (
                    s in base_data.services
                ), f"{s} in cloud_service_provider_services is not a valid service"

        for s in base_data.services:
            matched_to_csp = False

            for services in self.cloud_service_provider_services.values():
                if s in services:
                    matched_to_csp = True
                    break

            assert matched_to_csp is True

        # Validate min/max counts
        assert (
            self.min_cloud_service_provider_count >= 0
        ), "min_cloud_service_provider_count is negative"
        assert (
            self.max_cloud_service_provider_count >= 0
        ), "max_cloud_service_provider_count is negative"
        assert (
            self.min_cloud_service_provider_count
            <= self.max_cloud_service_provider_count
        ), "min_cloud_service_provider_count must be smaller or equal than max_cloud_service_provider_count"
