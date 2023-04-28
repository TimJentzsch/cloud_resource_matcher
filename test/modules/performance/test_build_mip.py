"""Tests for the build MIP step of the performance module."""
from optiframe import Optimizer
from pulp import LpMinimize

from cloud_resource_matcher.modules.base import BaseData, base_module
from cloud_resource_matcher.modules.performance import PerformanceData, performance_module
from cloud_resource_matcher.modules.service_limits import service_limits_module, ServiceLimitsData
from test.framework import Expect


OPTIMIZER = Optimizer("test_performance", sense=LpMinimize).add_modules(
    base_module, performance_module
)


def test_with_sufficient_resources() -> None:
    """The CS has enough resources to host the CR."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        ),
        PerformanceData(
            performance_criteria=["vCPU", "RAM"],
            performance_demand={("cr_0", "vCPU"): 8, ("cr_0", "RAM"): 3},
            performance_supply={("cs_0", "vCPU"): 8, ("cs_0", "RAM"): 4},
            cost_per_unit={},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_cs_instance_count({"cs_0": 1}).test()


def test_with_insufficient_performance() -> None:
    """The only CS does not have enough RAM for the CR."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        ),
        PerformanceData(
            performance_criteria=["vCPU", "RAM"],
            performance_demand={("cr_0", "vCPU"): 8, ("cr_0", "RAM"): 3},
            performance_supply={("cs_0", "vCPU"): 8, ("cs_0", "RAM"): 2},
            cost_per_unit={},
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_resource_matching() -> None:
    """Each CR has one CS matching its requirements exactly.

    There is only one valid matching: Assigning each CR to their matching CS.
    """
    count = 100

    optimizer = (
        Optimizer("test_performance", sense=LpMinimize)
        .add_modules(base_module, performance_module, service_limits_module)
        .initialize(
            BaseData(
                cloud_resources=[f"cr_{cr}" for cr in range(count)],
                cloud_services=[f"cs_{cs}" for cs in range(count)],
                cr_to_cs_list={
                    f"cr_{cr}": [f"cs_{cs}" for cs in range(count)] for cr in range(count)
                },
                # Arbitrary costs to make sure the constraints are actually enforced
                cs_to_base_cost={
                    f"cs_{cs}": (cs + 4) % 7 + (cs % 3) * (cs % 10) for cs in range(count)
                },
                cr_to_instance_demand={f"cr_{cr}": 1 for cr in range(count)},
            ),
            PerformanceData(
                performance_criteria=["RAM"],
                performance_demand={(f"cr_{cr}", "RAM"): cr for cr in range(count)},
                performance_supply={(f"cs_{cs}", "RAM"): cs for cs in range(count)},
                cost_per_unit={},
            ),
            ServiceLimitsData(
                cs_to_instance_limit={f"cs_{cs}": 1 for cs in range(count)},
                cr_to_max_instance_demand={f"cr_{cr}": 1 for cr in range(count)},
            ),
        )
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching(
        {(f"cr_{i}", f"cs_{i}"): 1 for i in range(count)}
    ).test()


def test_cheap_insufficient_cs() -> None:
    """There are two CSs, but the cheaper one has insufficient resources."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0", "cs_1"],
            cr_to_cs_list={"cr_0": ["cs_0", "cs_1"]},
            # Arbitrary costs to make sure the constraints are actually enforced
            cs_to_base_cost={"cs_0": 2, "cs_1": 10},
            cr_to_instance_demand={"cr_0": 1},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("cr_0", "RAM"): 3},
            performance_supply={("cs_0", "RAM"): 2, ("cs_1", "RAM"): 3},
            cost_per_unit={},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching({("cr_0", "cs_1"): 1}).with_cost(
        10
    ).test()


def test_allowed_incomplete_data() -> None:
    """Make sure that the user is allowed to leave data undefined where it makes sense."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        ),
        # Leave min requirements undefined
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={},
            performance_supply={("cs_0", "RAM"): 1},
            cost_per_unit={},
        ),
    )

    Expect(optimizer).to_be_feasible()


def test_should_work_with_higher_cr_and_time_to_instance_demand() -> None:
    """Some cloud resources have a demand higher than 1."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 2},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("cr_0", "RAM"): 3},
            performance_supply={("cs_0", "RAM"): 3},
            cost_per_unit={},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cr_to_cs_matching({("cr_0", "cs_0"): 2})


def test_should_be_infeasible_if_not_enough_cs_instances_can_be_bought() -> None:
    """Test that the problem is infeasible if not enough instances can be bought.

    There is demand for two CRs, which each occupy the CS fully.
    But only one instance of the CS may be bought.
    """
    optimizer = (
        Optimizer("test_performance", sense=LpMinimize)
        .add_modules(base_module, performance_module, service_limits_module)
        .initialize(
            BaseData(
                cloud_resources=["cr_0"],
                cloud_services=["cs_0"],
                cr_to_cs_list={"cr_0": ["cs_0"]},
                cs_to_base_cost={"cs_0": 1},
                cr_to_instance_demand={"cr_0": 2},
            ),
            PerformanceData(
                performance_criteria=["RAM"],
                performance_demand={("cr_0", "RAM"): 1},
                performance_supply={("cs_0", "RAM"): 1},
                cost_per_unit={},
            ),
            ServiceLimitsData(
                cs_to_instance_limit={"cs_0": 1}, cr_to_max_instance_demand={"cr_0": 2}
            ),
        )
    )

    Expect(optimizer).to_be_infeasible().test()


def test_should_include_performance_cost_in_objective() -> None:
    """One performance criterion has a cost which must be included in the objective."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 5},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("cr_0", "RAM"): 2},
            performance_supply={("cs_0", "RAM"): 5},
            cost_per_unit={("cs_0", "RAM"): 3},
        ),
    )

    # 5 * 1 from the base cost and 5 * 2 * 3 = 30 for the performance cost
    Expect(optimizer).to_be_feasible().with_cost(35).test()
