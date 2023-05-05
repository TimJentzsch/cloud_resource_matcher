"""Implementation of the build MIP step for the performance module."""
from optiframe import MipConstructionTask
from pulp import LpProblem, lpSum

from cloud_resource_matcher.modules.base import BaseData, BaseMipData

from .data import PerformanceData


class MipConstructionPerformanceTask(MipConstructionTask[None]):
    """A task to modify the MIP for the performance module."""

    problem: LpProblem
    base_data: BaseData
    performance_data: PerformanceData
    base_mip_data: BaseMipData

    def __init__(
        self,
        base_data: BaseData,
        performance_data: PerformanceData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ) -> None:
        self.base_data = base_data
        self.performance_data = performance_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def construct_mip(self) -> None:
        """Modify the MIP for the performance module.

        The constraints are enforced entirely in the pre-processing step.
        The MIP only needs to be adjusted to add the cost to the objective.
        """
        # Pay for the performance used by the cloud resources
        self.problem.objective += lpSum(
            self.base_mip_data.var_cr_to_cs_matching[cr, cs]
            * self.base_data.cr_to_instance_demand[cr]
            * self.performance_data.performance_demand[cr, pc]
            * self.performance_data.cost_per_unit[cs, pc]
            for cr in self.base_data.cloud_resources
            for cs in self.base_data.cr_to_cs_list[cr]
            for pc in self.performance_data.performance_criteria
            if (cs, pc) in self.performance_data.cost_per_unit.keys()
            and (cr, pc) in self.performance_data.performance_demand.keys()
        )
