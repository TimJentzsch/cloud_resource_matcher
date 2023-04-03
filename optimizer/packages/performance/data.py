from dataclasses import dataclass

from optimizer.packages.base.data import CloudService, CloudResource


PerformanceCriterion = str


@dataclass
class PerformanceData:
    # The available performance criteria, e.g. number of vCPUs or amount of RAM
    performance_criteria: list[PerformanceCriterion]

    # The demand a VM has for a given performance criterion
    # E.g. the number of vCPUs a VM needs to execute its workflows
    performance_demand: dict[tuple[CloudResource, PerformanceCriterion], int]

    # The supply a CS has of a given performance criterion
    # E.g. the number of vCPUs a CS offers
    performance_supply: dict[tuple[CloudService, PerformanceCriterion], int]
