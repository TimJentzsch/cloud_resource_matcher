"""The data for the multi cloud module."""
from dataclasses import dataclass

from cloud_resource_matcher.modules.base.data import CloudService, Cost

# The identifier for a cloud service provider such as AWS, Google Cloud or Azure.
# Commonly abbreviated as 'CSP'.
CloudServiceProvider = str


@dataclass
class MultiCloudData:
    """The data for the multi cloud module.

    Can be used to specify the different cloud service providers
    and the services they offer.
    It can be enforced that a minimum or maximum number of CSPs must be used.
    Additionally, migration costs can be specified.
    """

    # The identifiers of available cloud service providers.
    cloud_service_providers: list[CloudServiceProvider]

    # The map from cloud service providers to the cloud services that belong to them.
    # Must be specified for every CSP.
    csp_to_cs_list: dict[CloudServiceProvider, list[CloudService]]

    # The minimum number of cloud service providers that have to be used.
    min_csp_count: int

    # The maximum number of cloud service providers that can be used.
    max_csp_count: int

    # A map from cloud service providers to their usage cost.
    # This can be used to model migration or training costs.
    # Must be specified for every CSP.
    csp_to_cost: dict[CloudServiceProvider, Cost]
