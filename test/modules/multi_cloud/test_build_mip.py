"""Tests for the build MIP step of the multi cloud module."""
from test.framework import Expect

from optiframe import Optimizer
from pulp import LpMinimize

from cloud_resource_matcher.modules.base import BaseData, base_module
from cloud_resource_matcher.modules.multi_cloud import MultiCloudData, multi_cloud_module

OPTIMIZER = Optimizer("test_multi_cloud", sense=LpMinimize).add_modules(
    base_module, multi_cloud_module
)


def test_min_csp_count_constraint_matching() -> None:
    """Test that the min_csp_count influences the matching decision.

    There are two CSPs, one cheap and one expensive.
    To respect the min CSP count constraint, both CSPs have to be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1", "cs_2"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1", "cs_2"]},
            cs_to_base_cost={"cs_0": 1, "cs_1": 1, "cs_2": 10},
            cr_to_instance_demand={"cr_0": 1, "cr_1": 1},
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
        {"cr_0": "cs_0", "cr_1": "cs_2"}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 1}).test()


def test_max_csp_count_constraint_matching() -> None:
    """Test that the max_csp_count influences the matching decision.

    There are two CSPs, it would be cheapest to use both of them.
    To respect the max CSP count constraint, only one CSP can be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0", "cr_1"],
            cloud_services=["cs_0", "cs_1", "cs_2"],
            cr_to_cs_list={"cr_0": ["cs_0"], "cr_1": ["cs_1", "cs_2"]},
            cs_to_base_cost={"cs_0": 10, "cs_1": 10, "cs_2": 1},
            cr_to_instance_demand={"cr_0": 1, "cr_1": 1},
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
        {"cr_0": "cs_0", "cr_1": "cs_1"}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 0}).test()


def test_min_csp_count_constraint_infeasible() -> None:
    """Two CSPs have to be used, but there is only one CSP."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 10},
            cr_to_instance_demand={"cr_0": 1},
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
            cr_to_instance_demand={"cr_0": 1, "cr_1": 1},
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


def test_csp_objective() -> None:
    """There are two CSPs, one has cheaper cloud services, but a higher migration cost."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0", "cs_1"]},
            cs_to_base_cost={"cs_0": 10, "cs_1": 5},
            cr_to_instance_demand={"cr_0": 1},
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

    Expect(optimizer).to_be_feasible().with_cost(11).with_cr_to_cs_matching({"cr_0": "cs_0"}).test()
