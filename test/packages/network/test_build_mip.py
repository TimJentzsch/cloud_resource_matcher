from optiframe import Optimizer
from pulp import LpMinimize

from optimizer.packages.base import BaseData, base_package
from optimizer.packages.network import NetworkData, network_package
from test.framework import Expect


OPTIMIZER = (
    Optimizer("test_network", sense=LpMinimize)
    .add_package(base_package)
    .add_package(network_package)
)


def test_should_pay_for_cr_location_costs() -> None:
    """
    Ensure that the cost of traffic between CRs and specific locations is paid for.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 3},
        ),
        NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 3},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 2},
        ),
    )

    # Make sure the network costs are included in the total costs
    # demand * service base cost + demand * traffic * traffic cost
    Expect(optimizer).to_be_feasible().with_cost(3 * 5 + 3 * 3 * 2).test()


def test_should_be_infeasible_if_max_latency_is_violated() -> None:
    """
    The cloud resource can only be placed in a location where the max latency
    can't be respected.
    """
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_1"): 5},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_1"): 1},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_should_choose_matching_that_respects_max_latency() -> None:
    """The CR can be placed in two locations, but only one has low enough latency."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0", "cs_1"]},
            cs_to_base_cost={"cs_0": 5, "cs_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"cs_0": "loc_0", "cs_1": "loc_1"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 5},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 1},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching({("cr_0", "cs_0", 0): 1}).test()


def test_should_calculate_service_deployments_for_cr_pairs() -> None:
    """Two CRs are connected and need to be placed on two different cloud services."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1"]},
            cs_to_base_cost={"cs_0": 5, "cs_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_1", 0): 3},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"cs_0": "loc_0", "cs_1": "loc_1"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={
                ("cr_0", "cr_1"): 2,
                ("cr_1", "cr_0"): 1,
            },
            cr_and_loc_to_traffic={},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1, ("cr_1", "cs_1", 0): 3}
    ).with_variable_values(
        {
            "cr_pair_cs_deployment(cr_0,cs_0,cr_1,cs_1)": 1,
            "cr_pair_cs_deployment(cr_1,cs_1,cr_0,cs_0)": 1,
        }
    ).test()


def test_should_consider_latency_for_cr_to_cr_connections() -> None:
    """One of the connections between two CRs violates the maximum latency."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1"]},
            cs_to_base_cost={"cs_0": 5, "cs_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_1", 0): 1},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"cs_0": "loc_0", "cs_1": "loc_1"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={("cr_0", "cr_1"): 5},
            cr_and_cr_to_traffic={
                ("cr_0", "cr_1"): 1,
            },
            cr_and_loc_to_traffic={},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_infeasible().test()
