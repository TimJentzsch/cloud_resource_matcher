from dataclasses import dataclass
from typing import List, Dict

from optimizer.data import Service, CloudServiceProvider


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
