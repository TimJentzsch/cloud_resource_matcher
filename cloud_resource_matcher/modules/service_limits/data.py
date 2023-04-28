"""The data for the service limits module."""
from dataclasses import dataclass

from cloud_resource_matcher.modules.base.data import CloudService


@dataclass
class ServiceLimitsData:
    """The data for the service limits module."""

    # A map from cloud services to the maximum number of available instances.
    cs_to_instance_limit: dict[CloudService, int]

    # A map from cloud resources to the maximum number of instance they need at the SAME TIME.
    # This is in contrast to BaseData.cr_to_instance_demand, which specifies the total
    # demand over the whole optimization time period.
    cr_to_max_instance_demand: dict[CloudService, int]
