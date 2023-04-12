from dataclasses import dataclass


# Any resource that needs to be deployed to the cloud (e.g. virtual machines).
# Often abbreviated as 'CR'.
CloudResource = str

# A service offered by the cloud service provider that can host cloud resources.
# Often abbreviated as 'CS'.
CloudService = str

# The number of time units (e.g. hours)
TimeUnit = int

# A cost unit, e.g. € or $.
Cost = float


@dataclass
class BaseData:
    # The identifiers of available cloud resources
    cloud_resources: list[CloudResource]

    # The identifiers of offered cloud services.
    cloud_services: list[CloudService]

    # A map from cloud resources to the cloud services they can use.
    cr_to_cs_list: dict[CloudResource, list[CloudService]]

    # A map from cloud services to their fixed base cost.
    # The cost is given per instance and per time unit.
    cs_to_base_cost: dict[CloudService, Cost]

    # The discrete units of time when a decision can be made.
    time: list[TimeUnit]

    # A map from a cloud resource and a point in time to the
    # number of instances needed at that time.
    cr_and_time_to_instance_demand: dict[tuple[CloudResource, TimeUnit], int]
