from optimizer.data import BaseData
from optimizer.model import Model
from test.framework import Expect


def test_one_vm_one_service_trivial_solution():
    """One VM has one valid service and has to match to it."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": ["s_1"]},
            service_base_costs={"s_1": 5},
        )
    )

    Expect(model).to_be_feasible().with_cost(5).with_vm_service_matching(
        {"vm_1": "s_1"}
    ).test()


def test_only_one_valid_matching():
    """Every VM has only one valid service."""
    COUNT = 100

    model = Model(
        BaseData(
            virtual_machines=[f"vm_{v}" for v in range(COUNT)],
            services=[f"s_{s}" for s in range(COUNT)],
            virtual_machine_services={f"vm_{i}": [f"s_{i}"] for i in range(COUNT)},
            service_base_costs={f"s_{s}": s for s in range(COUNT)},
        )
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {f"vm_{i}": f"s_{i}" for i in range(COUNT)}
    ).test()


def test_no_valid_systems_for_vm():
    """There are no valid services for the only VM."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": []},
            service_base_costs={"s_1": 5},
        )
    )

    Expect(model).to_be_infeasible().with_variables(set(), exclusive=True).test()
