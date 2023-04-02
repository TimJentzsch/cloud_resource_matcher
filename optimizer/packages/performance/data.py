from dataclasses import dataclass
from typing import Dict

from optimizer.packages.base.data import Service, VirtualMachine
from optimizer.packages.base import BaseData


PerformanceCriterion = str


@dataclass
class PerformanceData:
    # The available performance criteria, e.g. number of vCPUs or amount of RAM
    performance_criteria: list[PerformanceCriterion]

    # The demand a VM has for a given performance criterion
    # E.g. the number of vCPUs a VM needs to execute its workflows
    performance_demand: dict[(VirtualMachine, PerformanceCriterion), int]

    # The supply a CS has of a given performance criterion
    # E.g. the number of vCPUs a CS offers
    performance_supply: dict[(Service, PerformanceCriterion), int]

    def validate(self, base_data: BaseData) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate performance_demand
        for (vm, pc) in self.performance_demand.items():
            assert vm in base_data.virtual_machines, f"{vm} in performance_demand is not a valid VM"
            assert (
                pc in self.performance_criteria
            ), f"{pc} in performance_demand is not a valid performance criterion"

        # Validate performance_supply
        for (cs, pc) in self.performance_supply.items():
            assert cs in base_data.services, f"{cs} in performance_supply is not a valid CS"
            assert (
                pc in self.performance_criteria
            ), f"{pc} in performance_supply is not a valid performance criterion"
