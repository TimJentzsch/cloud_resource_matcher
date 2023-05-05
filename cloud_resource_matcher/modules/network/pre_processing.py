"""Implementation of the pre-processing step for the network module."""
from optiframe import PreProcessingTask

from cloud_resource_matcher.modules.base import BaseData
from cloud_resource_matcher.modules.network import NetworkData


class PreProcessingNetworkTask(PreProcessingTask[BaseData]):
    """A task to apply pre-processing techniques to the network module."""

    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def pre_process(self) -> BaseData:
        """Enforce the latency requirements for the network module.

        Removes CSs from list of applicable CSs if the corresponding CR cannot support
        the latency of the CS to a given location.
        This only implements the maximum latency requirements for CR -> location connections.
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
