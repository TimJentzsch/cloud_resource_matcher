from dataclasses import dataclass

from optimizer.packages.base.data import CloudService


@dataclass
class ServiceLimitsData:
    # A map from cloud services to the maximum number of available instances.
    cs_to_instance_limit: dict[CloudService, int]

    # A map from cloud resources to the maximum number of instance they need at the SAME TIME.
    # This is in contrast to BaseData.cr_to_instance_demand, which specifies the total
    # demand over the whole optimization time period.
    cr_to_max_instance_demand: dict[CloudService, int]
