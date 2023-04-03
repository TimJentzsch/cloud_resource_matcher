from optiframe import Optimizer
from optimizer.packages.base import BaseData, base_package
from test.framework import Expect

OPTIMIZER = Optimizer("test_base").add_package(base_package)


def test_one_vm_one_service_trivial_solution() -> None:
    """One VM has one valid service and has to match to it."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1}
    ).test()


def test_only_one_valid_matching() -> None:
    """Every VM has only one valid service."""
    count = 100

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=[f"vm_{v}" for v in range(count)],
            cloud_services=[f"s_{s}" for s in range(count)],
            cr_to_cs_list={f"vm_{i}": [f"s_{i}"] for i in range(count)},
            cs_to_base_cost={f"s_{s}": s for s in range(count)},
            time=[0],
            cr_and_time_to_instance_demand={(f"vm_{v}", 0): 1 for v in range(count)},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_no_valid_systems_for_vm() -> None:
    """There are no valid cloud_cloud_services for the only VM."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": []},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_infeasible().test()


def test_one_vm_multiple_time_units() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0, 1],
            cr_and_time_to_instance_demand={("vm_0", 0): 1, ("vm_0", 1): 1},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(10).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_0", "s_0", 1): 1}
    ).test()


def test_one_vm_multiple_time_units_varying_demand() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[0, 1, 2],
            cr_and_time_to_instance_demand={("vm_0", 0): 5, ("vm_0", 1): 3, ("vm_0", 2): 2},
            cs_to_instance_limit={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5 + 3 + 2).with_vm_service_matching(
        {("vm_0", "s_0", 0): 5, ("vm_0", "s_0", 1): 3, ("vm_0", "s_0", 2): 2}
    ).test()
