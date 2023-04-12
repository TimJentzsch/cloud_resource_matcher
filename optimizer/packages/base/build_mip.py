from dataclasses import dataclass

from optiframe.framework.tasks import BuildMipTask
from pulp import LpVariable, LpProblem, LpBinary, lpSum

from .data import BaseData, CloudService, CloudResource

VarCrToCsMatching = dict[tuple[CloudResource, CloudService], LpVariable]
CsToCrList = dict[CloudService, set[CloudResource]]


@dataclass
class BaseMipData:
    # Which cloud resource should be deployed on which cloud service?
    var_cr_to_cs_matching: VarCrToCsMatching
    # Which cloud services are used at all?
    var_cs_used: dict[CloudService, LpVariable]


class BuildMipBaseTask(BuildMipTask[BaseMipData]):
    base_data: BaseData
    problem: LpProblem

    def __init__(self, base_data: BaseData, problem: LpProblem):
        self.base_data = base_data
        self.problem = problem

    def execute(self) -> BaseMipData:
        # Pre-compute which cloud services can host which cloud resources
        cs_to_cr_list: CsToCrList = {
            cs: set(
                cr
                for cr in self.base_data.cloud_resources
                if cs in self.base_data.cr_to_cs_list[cr]
            )
            for cs in self.base_data.cloud_services
        }

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

        # Has cloud service cs been purchased at all?
        var_cs_used: dict[CloudService, LpVariable] = {
            cs: LpVariable(f"service_used({cs})", cat=LpBinary)
            for cs in self.base_data.cloud_services
        }

        # Calculate var_cs_used
        for cs in self.base_data.cloud_services:
            self.problem += (
                var_cs_used[cs] <= lpSum(var_cr_to_cs_matching[cr, cs] for cr in cs_to_cr_list[cs]),
                f"connect_cr_to_cs_matching_and_cs_used({cs})",
            )

        # Base costs for used cloud services
        self.problem.objective += lpSum(
            var_cr_to_cs_matching[cr, cs]
            * self.base_data.cr_and_time_to_instance_demand[cr, t]
            * self.base_data.cs_to_base_cost[cs]
            for cr in self.base_data.cloud_resources
            for cs in self.base_data.cr_to_cs_list[cr]
            for t in self.base_data.time
        )

        return BaseMipData(
            var_cr_to_cs_matching=var_cr_to_cs_matching,
            var_cs_used=var_cs_used,
        )
