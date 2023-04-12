from optiframe import Optimizer
from pulp import LpMinimize

from optimizer.packages.base import BaseData, base_package
from optimizer.packages.multi_cloud import MultiCloudData, multi_cloud_package
from test.framework import Expect


OPTIMIZER = (
    Optimizer("test_multi_cloud", sense=LpMinimize)
    .add_package(base_package)
    .add_package(multi_cloud_package)
)


def test_min_csp_count_constraint_matching() -> None:
    """There are two CSPs, one cheap and one expensive.
    To respect the min CSP count constraint, both CSPs have to be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1", "cs_2"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1", "cs_2"]},
            cs_to_base_cost={"cs_0": 1, "cs_1": 1, "cs_2": 10},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_1", 0): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            csp_to_cs_list={
                "csp_0": ["cs_0", "cs_1"],
                "csp_1": ["cs_2"],
            },
            min_csp_count=2,
            max_csp_count=100,
            csp_to_cost={"csp_0": 0, "csp_1": 0},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(11).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1, ("cr_1", "cs_2", 0): 1}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 1}).test()


def test_max_csp_count_constraint_matching() -> None:
    """There are two CSPs, it would be cheapest to use both of them.
    To respect the max CSP count constraint, only one CSP can be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1", "cs_2"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1", "cs_2"]},
            cs_to_base_cost={"cs_0": 10, "cs_1": 10, "cs_2": 1},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_1", 0): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            csp_to_cs_list={
                "csp_0": ["cs_0", "cs_1"],
                "csp_1": ["cs_2"],
            },
            min_csp_count=0,
            max_csp_count=1,
            csp_to_cost={"csp_0": 0, "csp_1": 0},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(20).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1, ("cr_1", "cs_1", 0): 1}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 0}).test()


def test_min_csp_count_constraint_infeasible() -> None:
    """Two CSPs have to be used, but there is only one CSP."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 10},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            min_csp_count=2,
            max_csp_count=100,
            csp_to_cost={"csp_0": 0},
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_max_csp_count_constraint_infeasible() -> None:
    """Only one CSP must be used, but it's only possible with two."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1"]},
            cs_to_base_cost={"cs_0": 10, "cs_1": 10},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_1", 0): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            csp_to_cs_list={"csp_0": ["cs_0"], "csp_1": ["cs_1"]},
            min_csp_count=0,
            max_csp_count=1,
            csp_to_cost={"csp_0": 0, "csp_1": 0},
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_with_multiple_time_points() -> None:
    """Make sure that the CSP constraints also work for multiple time points."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 10},
            time=[0, 1],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_0", 1): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            min_csp_count=1,
            max_csp_count=1,
            csp_to_cost={"csp_0": 0},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1, ("cr_0", "cs_0", 1): 1}
    ).with_cost(20).test()


def test_csp_objective() -> None:
    """
    There are two CSPs, one has cheaper cloud services, but a higher migration cost.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0", "cs_1"]},
            cs_to_base_cost={"cs_0": 10, "cs_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            csp_to_cs_list={
                "csp_0": ["cs_0"],
                "csp_1": ["cs_1"],
            },
            min_csp_count=0,
            max_csp_count=1,
            csp_to_cost={"csp_0": 1, "csp_1": 10},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(11).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1}
    ).test()
