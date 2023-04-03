from dataclasses import dataclass

from optimizer.packages.base.data import CloudService, Cost


CloudServiceProvider = str


@dataclass
class MultiCloudData:
    # The available cloud service providers
    cloud_service_providers: list[CloudServiceProvider]

    # The cloud_services each cloud service provider offers
    cloud_service_provider_services: dict[CloudServiceProvider, list[CloudService]]

    # The minimum number of cloud service providers that have to be used
    min_cloud_service_provider_count: int

    # The maximum number of cloud service providers that can be used
    max_cloud_service_provider_count: int

    # How much does it cost to use each CSP?
    # This can be used to model migration or training costs
    # Must be specified for every CSP
    cloud_service_provider_costs: dict[CloudServiceProvider, Cost]
