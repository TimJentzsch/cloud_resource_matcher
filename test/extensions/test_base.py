from optiframe import Optimizer
from optimizer.packages.base import BaseData, BASE_PACKAGE
from test.framework import Expect

OPTIMIZER = Optimizer("test_base").add_package(BASE_PACKAGE)


def test_one_vm_one_service_trivial_solution() -> None:
    """One VM has one valid service and has to match to it."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
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
            virtual_machines=[f"vm_{v}" for v in range(count)],
            services=[f"s_{s}" for s in range(count)],
            virtual_machine_services={f"vm_{i}": [f"s_{i}"] for i in range(count)},
            service_base_costs={f"s_{s}": s for s in range(count)},
            time=[0],
            virtual_machine_demand={(f"vm_{v}", 0): 1 for v in range(count)},
            max_service_instances={},
        )
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_no_valid_systems_for_vm() -> None:
    """There are no valid services for the only VM."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": []},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )
    )

    Expect(optimizer).to_be_infeasible().test()


def test_one_vm_multiple_time_units() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0, 1],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_0", 1): 1},
            max_service_instances={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(10).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_0", "s_0", 1): 1}
    ).test()


def test_one_vm_multiple_time_units_varying_demand() -> None:
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0, 1, 2],
            virtual_machine_demand={("vm_0", 0): 5, ("vm_0", 1): 3, ("vm_0", 2): 2},
            max_service_instances={},
        )
    )

    Expect(optimizer).to_be_feasible().with_cost(5 + 3 + 2).with_vm_service_matching(
        {("vm_0", "s_0", 0): 5, ("vm_0", "s_0", 1): 3, ("vm_0", "s_0", 2): 2}
    ).test()
