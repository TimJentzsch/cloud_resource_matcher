"""Tests for the build MIP step of the base module."""
from optiframe import Optimizer
from pulp import LpMinimize

from cloud_resource_matcher.modules.base import BaseData, base_module
from test.framework import Expect

OPTIMIZER = Optimizer("test_base", sense=LpMinimize).add_modules(base_module)


def test_one_cr_one_cs_trivial_solution() -> None:
    """One CR has one valid CS and has to match to it."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_cr_to_cs_matching(
        {("cr_0", "cs_0"): 1}
    ).test()


def test_only_one_valid_matching() -> None:
    """Every CR has only one valid CS."""
    count = 100

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=[f"cr_{v}" for v in range(count)],
            cloud_services=[f"cs_{s}" for s in range(count)],
            cr_to_cs_list={f"cr_{i}": [f"cs_{i}"] for i in range(count)},
            cs_to_base_cost={f"cs_{s}": s for s in range(count)},
            cr_to_instance_demand={f"cr_{v}": 1 for v in range(count)},
        )
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching(
        {(f"cr_{i}", f"cs_{i}"): 1 for i in range(count)}
    ).test()


def test_no_valid_cs_for_cr() -> None:
    """There are no valid CS for the only CR."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": []},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )
    )

    Expect(optimizer).to_be_infeasible().test()
