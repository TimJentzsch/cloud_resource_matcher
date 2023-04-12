from dataclasses import dataclass

from optimizer.packages.base.data import CloudService


@dataclass
class ServiceLimitsData:
    # A map from cloud services to the maximum number of available instances.
    cs_to_instance_limit: dict[CloudService, int]
