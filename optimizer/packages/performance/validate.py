from optiframe import Task

from optimizer.packages.base import BaseData
from .data import PerformanceData


class ValidatePerformanceTask(Task[None]):
    base_data: BaseData
    performance_data: PerformanceData

    def __init__(self, base_data: BaseData, performance_data: PerformanceData):
        self.base_data = base_data
        self.performance_data = performance_data

    def execute(self) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate performance_demand
        for (cr, pc) in self.performance_data.performance_demand.keys():
            assert (
                cr in self.base_data.cloud_resources
            ), f"{cr} in performance_demand is not a valid CR"
            assert (
                pc in self.performance_data.performance_criteria
            ), f"{pc} in performance_demand is not a valid performance criterion"

        # Validate performance_supply
        for (cs, pc) in self.performance_data.performance_supply.keys():
            assert (
                cs in self.base_data.cloud_services
            ), f"{cs} in performance_supply is not a valid CS"
            assert (
                pc in self.performance_data.performance_criteria
            ), f"{pc} in performance_supply is not a valid performance criterion"

        # The supply for each criterion must be specified for all CSs
        for cs in self.base_data.cloud_services:
            for pc in self.performance_data.performance_criteria:
                assert (
                    cs,
                    pc,
                ) in self.performance_data.performance_supply.keys(), (
                    f"CS {cs} does not have its supply for {pc} defined"
                )
