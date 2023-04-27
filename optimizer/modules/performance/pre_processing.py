from optiframe.framework.tasks import PreProcessingTask

from optimizer.modules.base import BaseData
from optimizer.modules.performance import PerformanceData


class PreProcessingPerformanceTask(PreProcessingTask[BaseData]):
    base_data: BaseData
    performance_data: PerformanceData

    def __init__(self, base_data: BaseData, performance_data: PerformanceData):
        self.base_data = base_data
        self.performance_data = performance_data

    def execute(self) -> BaseData:
        """
        Remove CSs from the list of applicable CS if they do not satisfy the
        performance requirements of a CR.
        """
        for (cr, pc), demand in self.performance_data.performance_demand.items():
            cs_list = self.base_data.cr_to_cs_list[cr]

            # The CSs that satisfy the performance criteria
            performant_cs = [
                cs for cs in cs_list if self.performance_data.performance_supply[(cs, pc)] >= demand
            ]

            # Update the applicable CSs
            self.base_data.cr_to_cs_list[cr] = performant_cs

        return self.base_data
