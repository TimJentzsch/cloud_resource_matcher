"""Implementation of the build MIP step for the multi cloud module."""
from dataclasses import dataclass

from optiframe.framework.tasks import BuildMipTask
from pulp import LpBinary, LpProblem, LpVariable, lpSum

from cloud_resource_matcher.modules.base import BaseData, BaseMipData

from .data import CloudServiceProvider, MultiCloudData


@dataclass
class MultiCloudMipData:
    """The data generated by the build MIP step for the multi cloud module.

    Includes the variables that have been added to the MIP.
    """

    var_csp_used: dict[CloudServiceProvider, LpVariable]


class BuildMipMultiCloudTask(BuildMipTask[MultiCloudMipData]):
    """A task to modify the MIP to implement the multi cloud module."""

    base_data: BaseData
    multi_cloud_data: MultiCloudData
    base_mip_data: BaseMipData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        multi_cloud_data: MultiCloudData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def execute(self) -> MultiCloudMipData:
        """Modify the MIP to implement the multi cloud module.

        This adds variables  to track which CSPs are used and enforces the corresponding
        requirements and objectives.
        """
        # Is cloud service provider csp used at all?
        var_csp_used: dict[CloudServiceProvider, LpVariable] = {
            csp: LpVariable(f"csp_used({csp})", cat=LpBinary)
            for csp in self.multi_cloud_data.cloud_service_providers
        }

        # Calculate csp_used values
        for csp in self.multi_cloud_data.cloud_service_providers:
            used_service_count = lpSum(
                self.base_mip_data.var_cr_to_cs_matching[cr, cs]
                for cr in self.base_data.cloud_resources
                for cs in self.base_data.cr_to_cs_list[cr]
                if cs in self.multi_cloud_data.csp_to_cs_list[csp]
            )

            self.problem += (
                var_csp_used[csp] <= used_service_count,
                f"csp_used_enforce_0({csp})",
            )

            for cr in self.base_data.cloud_resources:
                for cs in self.base_data.cr_to_cs_list[cr]:
                    if cs in self.multi_cloud_data.csp_to_cs_list[csp]:
                        self.problem += (
                            var_csp_used[csp] >= self.base_mip_data.var_cr_to_cs_matching[cr, cs],
                            f"csp_used_enforce_1({csp},{cr},{cs})",
                        )

        # Enforce minimum and maximum number of used CSPs
        self.problem.addConstraint(
            lpSum(var_csp_used[csp] for csp in self.multi_cloud_data.cloud_service_providers)
            >= self.multi_cloud_data.min_csp_count,
            "min_csp_count",
        )
        self.problem.addConstraint(
            lpSum(var_csp_used[csp] for csp in self.multi_cloud_data.cloud_service_providers)
            <= self.multi_cloud_data.max_csp_count,
            "max_csp_count",
        )

        # Add CSP cost to objective
        self.problem.objective += lpSum(
            var_csp_used[csp] * self.multi_cloud_data.csp_to_cost[csp]
            for csp in self.multi_cloud_data.cloud_service_providers
        )

        return MultiCloudMipData(var_csp_used)
