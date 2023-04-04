from optiframe import Optimizer
from optimizer.packages.base import BaseData, base_package
from test.framework import Expect

OPTIMIZER = Optimizer("test_base").add_package(base_package)


def test_one_cr_one_cs_trivial_solution() -> None:
    """One CR has one valid CS and has to match to it."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1}
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
            time=[0],
            cr_and_time_to_instance_demand={(f"cr_{v}", 0): 1 for v in range(count)},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching(
        {(f"cr_{i}", f"cs_{i}", 0): 1 for i in range(count)}
    ).test()


def test_no_valid_cs_for_cr() -> None:
    """There are no valid CS for the only CR."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": []},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_infeasible().test()


def test_one_cr_multiple_time_units() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            time=[0, 1],
            cr_and_time_to_instance_demand={("cr_0", 0): 1, ("cr_0", 1): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(10).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 1, ("cr_0", "cs_0", 1): 1}
    ).test()


def test_one_cr_multiple_time_units_varying_demand() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            time=[0, 1, 2],
            cr_and_time_to_instance_demand={("cr_0", 0): 5, ("cr_0", 1): 3, ("cr_0", 2): 2},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5 + 3 + 2).with_cr_to_cs_matching(
        {("cr_0", "cs_0", 0): 5, ("cr_0", "cs_0", 1): 3, ("cr_0", "cs_0", 2): 2}
    ).test()
