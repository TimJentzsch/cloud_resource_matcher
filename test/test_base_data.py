from optimizer.data import BaseData
from optimizer.model import Model
from test.framework import Expect


def test_no_valid_systems_for_vm():
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": []},
            service_base_costs={"s_1": 5},
        )
    )

    Expect(model).to_be_infeasible().test()
