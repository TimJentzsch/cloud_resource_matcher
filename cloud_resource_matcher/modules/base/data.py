"""The data for the base module."""
from dataclasses import dataclass

# Any resource that needs to be deployed to the cloud (e.g. virtual machines).
# Often abbreviated as 'CR'.
CloudResource = str

# A service offered by the cloud service provider that can host cloud resources.
# Often abbreviated as 'CS'.
CloudService = str

# The cost in any price unit, e.g. € or $.
Cost = float


@dataclass
class BaseData:
    """The data for the base module.

    This includes the most important information, such as the available
    cloud resources and cloud services and which services can be used
    for which resources.
    Flat (or upfront) costs for the cloud services can also be specified.
    """

    # The identifiers of available cloud resources.
    # Cloud resources are anything that can be deployed on the cloud.
    cloud_resources: list[CloudResource]

    # The identifiers of offered cloud services.
    cloud_services: list[CloudService]

    # A map from cloud resources to the cloud services they can use.
    cr_to_cs_list: dict[CloudResource, list[CloudService]]

    # A map from cloud services to their fixed base cost.
    # The cost is given per instance and per billing unit.
    cs_to_base_cost: dict[CloudService, Cost]

    # A map from a cloud resource to the number of instances needed
    # over the optimization time range.
    cr_to_instance_demand: dict[CloudResource, int]
