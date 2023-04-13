from dataclasses import dataclass

from optiframe.framework.tasks import BuildMipTask
from pulp import LpProblem, LpBinary, LpVariable, lpSum

from .data import NetworkData
from ..base.data import CloudService, CloudResource
from optimizer.packages.base import BaseData, BaseMipData


@dataclass
class NetworkMipData:
    # Is cr1 deployed to cs1 and cr2 deployed to cs2?
    var_cr_pair_cs_deployment: dict[
        tuple[CloudResource, CloudService, CloudResource, CloudService], LpVariable
    ]


class BuildMipNetworkTask(BuildMipTask[NetworkMipData]):
    base_data: BaseData
    network_data: NetworkData
    base_mip_data: BaseMipData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        network_data: NetworkData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.network_data = network_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def execute(self) -> NetworkMipData:
        connection_deployments = dict()

        # Pre-compute the possible deployments for CR pairs respecting the latency
        for (
            cr1,
            cr2,
        ) in self.network_data.cr_and_cr_to_traffic.keys():
            max_latency = self.network_data.cr_and_cr_to_max_latency.get((cr1, cr2))
            deployment_list = []

            for cs1 in self.base_data.cr_to_cs_list[cr1]:
                loc1 = self.network_data.cs_to_loc[cs1]

                for cs2 in self.base_data.cr_to_cs_list[cr2]:
                    loc2 = self.network_data.cs_to_loc[cs2]

                    if (
                        max_latency is None
                        or self.network_data.loc_and_loc_to_latency[(loc1, loc2)] <= max_latency
                    ):
                        deployment_list.append((cs1, cs2))

            connection_deployments[(cr1, cr2)] = deployment_list

        # Is there a cr1 -> cr2 connection where cr1 is deployed to cs1 and cr2 to cs2?
        var_cr_pair_cs_deployment: dict[
            tuple[CloudResource, CloudService, CloudResource, CloudService],
            LpVariable,
        ] = {
            (cr1, cs1, cr2, cs2): LpVariable(
                f"cr_pair_cs_deployment({cr1},{cs1},{cr2},{cs2})",
                cat=LpBinary,
            )
            for (cr1, cr2) in self.network_data.cr_and_cr_to_traffic.keys()
            for (cs1, cs2) in connection_deployments[(cr1, cr2)]
        }

        # Calculate deployments of cloud resource pairs
        for (
            cr1,
            cr2,
        ) in self.network_data.cr_and_cr_to_traffic.keys():
            # Every CR pair has one pair of cloud service connections
            self.problem += (
                lpSum(
                    var_cr_pair_cs_deployment[cr1, cs1, cr2, cs2]
                    for (cs1, cs2) in connection_deployments[(cr1, cr2)]
                )
                == 1
            )

            # If a CR has been deployed to a given CS, enforce this for the pair as well
            for (cs1, cs2) in connection_deployments[(cr1, cr2)]:
                self.problem += (
                    var_cr_pair_cs_deployment[cr1, cs1, cr2, cs2]
                    <= self.base_mip_data.var_cr_to_cs_matching[cr1, cs1]
                )
                self.problem += (
                    var_cr_pair_cs_deployment[cr1, cs1, cr2, cs2]
                    <= self.base_mip_data.var_cr_to_cs_matching[cr2, cs2]
                )

        # Pay for CR -> loc traffic
        self.problem.objective += lpSum(
            self.base_mip_data.var_cr_to_cs_matching[cr, cs]
            * self.base_data.cr_to_instance_demand[cr]
            * traffic
            * self.network_data.loc_and_loc_to_cost[self.network_data.cs_to_loc[cs], loc]
            for (
                cr,
                loc,
            ), traffic in self.network_data.cr_and_loc_to_traffic.items()
            for cs in self.base_data.cr_to_cs_list[cr]
        )

        # Pay for CR -> CR traffic
        self.problem.objective += lpSum(
            var_cr_pair_cs_deployment[cr1, cs1, cr2, cs2]
            * self.base_data.cr_to_instance_demand[cr1]
            * traffic
            * self.network_data.loc_and_loc_to_cost[
                self.network_data.cs_to_loc[cs1], self.network_data.cs_to_loc[cs2]
            ]
            for (
                cr1,
                cr2,
            ), traffic in self.network_data.cr_and_cr_to_traffic.items()
            for (cs1, cs2) in connection_deployments[(cr1, cr2)]
        )

        return NetworkMipData(var_cr_pair_cs_deployment)
