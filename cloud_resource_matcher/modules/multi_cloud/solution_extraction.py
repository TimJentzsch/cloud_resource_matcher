"""Implementation of the extract solution step for the multi cloud module."""
from dataclasses import dataclass

from optiframe import SolutionExtractionTask
from pulp import pulp

from .data import MultiCloudData
from .mip_construction import MultiCloudMipData


@dataclass
class MultiCloudSolution:
    """The solution for the multi cloud module.

    This allows you to easily determine which cloud service providers have been selected.
    """

    # Which cloud service providers have been selected in the solution?
    selected_csps: set[str]


class SolutionExtractionMultiCloudTask(SolutionExtractionTask[MultiCloudSolution]):
    """A task to extract the solution for the multi cloud module."""

    multi_cloud_data: MultiCloudData
    multi_cloud_mip_data: MultiCloudMipData

    def __init__(self, multi_cloud_data: MultiCloudData, multi_cloud_mip_data: MultiCloudMipData):
        self.multi_cloud_data = multi_cloud_data
        self.multi_cloud_mip_data = multi_cloud_mip_data

    def extract_solution(self) -> MultiCloudSolution:
        """Extract the solution for the multi cloud module.

        Determines which cloud service providers have been selected.
        """
        selected_csps: set[str] = set()

        for csp in self.multi_cloud_data.cloud_service_providers:
            value = round(pulp.value(self.multi_cloud_mip_data.var_csp_used[csp]))

            if value >= 1:
                selected_csps.add(csp)

        return MultiCloudSolution(selected_csps=selected_csps)
