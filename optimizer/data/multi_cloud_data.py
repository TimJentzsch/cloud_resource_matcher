from dataclasses import dataclass
from typing import List, Dict

from optimizer.data import Service, CloudServiceProvider
from optimizer.data.base_data import BaseData


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

    def validate(self, base_data: BaseData):
        """Validate the data for consistency."""
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

        assert (
            self.min_cloud_service_provider_count >= 0
        ), "min_cloud_service_provider_count is negative"
        assert (
            self.max_cloud_service_provider_count >= 0
        ), "max_cloud_service_provider_count is negative"
