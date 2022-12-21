from optimizer.data import BaseData
from optimizer.model import Model
from test.framework import Expect


def test_one_vm_one_service_trivial_solution():
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


def test_no_valid_systems_for_vm():
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": []},
            service_base_costs={"s_1": 5},
        )
    )

    Expect(model).to_be_infeasible().with_variables(set(), exclusive=True).test()
