from optiframe import Optimizer
from pulp import LpMinimize

from optimizer.packages.base import BaseData, base_package
from optimizer.packages.service_limits import service_limits_package, ServiceLimitsData
from test.framework import Expect

OPTIMIZER = (
    Optimizer("test_service_limits", sense=LpMinimize)
    .add_package(base_package)
    .add_package(service_limits_package)
)


def test_one_cr_one_cs_trivial_solution() -> None:
    """One CR has one valid CS and has to match to it."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_and_time_to_instance_demand={"cr_0": 1},
        ),
        ServiceLimitsData(cs_to_instance_limit={"cs_0": 1}),
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_cr_to_cs_matching(
        {("cr_0", "cs_0"): 1}
    ).test()


def test_infeasible_not_enough_cs_instances() -> None:
    """There is only 1 CS instance available, but 2 are needed."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_and_time_to_instance_demand={"cr_0": 2},
        ),
        ServiceLimitsData(cs_to_instance_limit={"cs_0": 1}),
    )

    Expect(optimizer).to_be_infeasible().test()
