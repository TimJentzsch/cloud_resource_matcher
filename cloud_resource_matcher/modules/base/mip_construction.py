"""Implementation of the MIP construction step for the base module."""
from dataclasses import dataclass

from optiframe import MipConstructionTask
from pulp import LpBinary, LpProblem, LpVariable, lpSum

from .data import BaseData, CloudResource, CloudService

VarCrToCsMatching = dict[tuple[CloudResource, CloudService], LpVariable]
CsToCrList = dict[CloudService, set[CloudResource]]


@dataclass
class BaseMipData:
    """The data generated by the build MIP step for the base module.

    Includes the variables that have been added to the MIP.
    """

    # Which cloud resource should be deployed on which cloud service?
    var_cr_to_cs_matching: VarCrToCsMatching


class MipConstructionBaseTask(MipConstructionTask[BaseMipData]):
    """A task to modify the MIP to implement the base module."""

    base_data: BaseData
    problem: LpProblem

    def __init__(self, base_data: BaseData, problem: LpProblem):
        self.base_data = base_data
        self.problem = problem

    def construct_mip(self) -> BaseMipData:
        """Modify the MIP to implement the base module.

        Adds the central variables to determine which CR to deploy on which CS.
        """
        # Assign cloud resource cr to cloud service cs at time t?
        # ASSUMPTION: Each cloud service instance can only be used by one cloud resource instance
        # ASSUMPTION: All instances of one cloud resource have to be deployed
        #   on the same service type
        var_cr_to_cs_matching: VarCrToCsMatching = {
            (cr, cs): LpVariable(f"cr_to_cs_matching({cr},{cs})", cat=LpBinary)
            for cr in self.base_data.cloud_resources
            for cs in self.base_data.cr_to_cs_list[cr]
        }

        # Satisfy cloud resource demands
        for cr in self.base_data.cloud_resources:
            self.problem += (
                lpSum(var_cr_to_cs_matching[cr, cs] for cs in self.base_data.cr_to_cs_list[cr])
                == 1,
                f"cr_demand({cr})",
            )

        # Base costs for used cloud services
        self.problem.objective += lpSum(
            var_cr_to_cs_matching[cr, cs]
            * self.base_data.cr_to_instance_demand[cr]
            * self.base_data.cs_to_base_cost[cs]
            for cr in self.base_data.cloud_resources
            for cs in self.base_data.cr_to_cs_list[cr]
        )

        return BaseMipData(
            var_cr_to_cs_matching=var_cr_to_cs_matching,
        )
