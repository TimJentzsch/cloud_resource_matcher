from optimizer.data.base_data import BaseData
from optimizer.model import Model
from test.framework import Expect


def test_one_vm_one_service_trivial_solution():
    """One VM has one valid service and has to match to it."""
    model = Model(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
        ).validate()
    )

    Expect(model).to_be_feasible().with_cost(5).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1}
    ).test()


def test_only_one_valid_matching():
    """Every VM has only one valid service."""
    count = 100

    model = Model(
        BaseData(
            virtual_machines=[f"vm_{v}" for v in range(count)],
            services=[f"s_{s}" for s in range(count)],
            virtual_machine_services={f"vm_{i}": [f"s_{i}"] for i in range(count)},
            service_base_costs={f"s_{s}": s for s in range(count)},
            time=[0],
            virtual_machine_demand={(f"vm_{v}", 0): 1 for v in range(count)},
        ).validate()
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_no_valid_systems_for_vm():
    """There are no valid services for the only VM."""
    model = Model(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": []},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
        ).validate()
    )

    Expect(model).to_be_infeasible().with_variables(
        {"service_instance_count(s_0,0)", "service_used(s_0,0)"}, exclusive=True
    ).test()


def test_one_vm_multiple_time_units():
    model = Model(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0, 1],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_0", 1): 1},
        ).validate()
    )

    Expect(model).to_be_feasible().with_cost(10).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_0", "s_0", 1): 1}
    ).test()


def test_one_vm_multiple_time_units_varying_demand():
    model = Model(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0, 1, 2],
            virtual_machine_demand={("vm_0", 0): 5, ("vm_0", 1): 3, ("vm_0", 2): 2},
        ).validate()
    )

    Expect(model).to_be_feasible().with_cost(3).with_vm_service_matching(
        {("vm_0", "s_0", 0): 5, ("vm_0", "s_0", 1): 3, ("vm_0", "s_0", 2): 2}
    ).test()
