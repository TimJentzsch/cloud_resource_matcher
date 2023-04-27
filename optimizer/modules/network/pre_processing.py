from optiframe.framework.tasks import PreProcessingTask

from optimizer.modules.base import BaseData
from optimizer.modules.network import NetworkData


class PreProcessingNetworkTask(PreProcessingTask[BaseData]):
    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def execute(self) -> BaseData:
        """
        Remove CS from list of applicable CS if the corresponding CR cannot support
        the latency of the CS to a given location.
        """
        for (cr, loc), max_latency in self.network_data.cr_and_loc_to_max_latency.items():
            cs_list = self.base_data.cr_to_cs_list[cr]

            # The CSs that satisfy the maximum latency criteria
            low_latency_cs = [
                cs
                for cs in cs_list
                if self.network_data.loc_and_loc_to_latency[(self.network_data.cs_to_loc[cs], loc)]
                <= max_latency
            ]

            # Update the applicable CSs
            self.base_data.cr_to_cs_list[cr] = low_latency_cs

        return self.base_data
