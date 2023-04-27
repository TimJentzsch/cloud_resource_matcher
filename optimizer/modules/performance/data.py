from dataclasses import dataclass

from optimizer.modules.base.data import CloudService, CloudResource, Cost

PerformanceCriterion = str


@dataclass
class PerformanceData:
    # The available performance criteria, e.g. number of vCPUs or amount of RAM
    performance_criteria: list[PerformanceCriterion]

    # The demand a VM has for a given performance criterion
    # E.g. the number of vCPUs a VM needs to execute its workflows
    performance_demand: dict[tuple[CloudResource, PerformanceCriterion], float]

    # The supply a CS has of a given performance criterion
    # E.g. the number of vCPUs a CS offers
    performance_supply: dict[tuple[CloudService, PerformanceCriterion], float]

    # The cost of a performance criterion for a cloud service.
    # The cost is given per unit used by the cloud resources.
    # The cost is further multiplied by the instance demand of the cloud resource.
    # If no cost is defined, `0` is assumed.
    cost_per_unit: dict[tuple[CloudService, PerformanceCriterion], Cost]
