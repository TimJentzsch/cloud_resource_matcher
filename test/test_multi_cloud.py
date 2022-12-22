from optimizer.data import BaseData, MultiCloudData
from optimizer.model import Model
from test.framework import Expect


def test_min_csp_count_constraint_matching():
    """There are two CSPs, one cheap and one expensive.
    To respect the min CSP count constraint, both CSPs have to be used.
    """
    model = Model(
        BaseData(
            virtual_machines=["vm_1", "vm_2"],
            services=["s_1", "s_2", "s_3"],
            virtual_machine_services={"vm_1": ["s_1"], "vm_2": ["s_2", "s_3"]},
            service_base_costs={"s_1": 1, "s_2": 1, "s_3": 10},
        )
    ).with_multi_cloud(
        MultiCloudData(
            cloud_service_providers=["csp_1", "csp_2"],
            cloud_service_provider_services={"csp_1": ["s_1", "s_2"], "csp_2": ["s_3"]},
            min_cloud_service_provider_count=2,
            max_cloud_service_provider_count=100,
        )
    )

    Expect(model).to_be_feasible().with_cost(11).with_vm_service_matching(
        {"vm_1": "s_1", "vm_2": "s_3"}
    ).with_variable_values({"csp_used(csp_1)": 1, "csp_used(csp_2)": 1}).test()


def test_max_csp_count_constraint_matching():
    """There are two CSPs, it would be cheapest to use most of them.
    To respect the max CSP count constraint, only one CSP can be used.
    """
    model = Model(
        BaseData(
            virtual_machines=["vm_1", "vm_2"],
            services=["s_1", "s_2", "s_3"],
            virtual_machine_services={"vm_1": ["s_1"], "vm_2": ["s_2", "s_3"]},
            service_base_costs={"s_1": 10, "s_2": 10, "s_3": 1},
        )
    ).with_multi_cloud(
        MultiCloudData(
            cloud_service_providers=["csp_1", "csp_2"],
            cloud_service_provider_services={"csp_1": ["s_1", "s_2"], "csp_2": ["s_3"]},
            min_cloud_service_provider_count=0,
            max_cloud_service_provider_count=1,
        )
    )

    Expect(model).to_be_feasible().with_cost(20).with_vm_service_matching(
        {"vm_1": "s_1", "vm_2": "s_2"}
    ).with_variable_values({"csp_used(csp_1)": 1, "csp_used(csp_2)": 0}).test()


def test_min_csp_count_constraint_infeasible():
    """Two CSPs have to be used, but there is only one CSP."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": ["s_1"]},
            service_base_costs={"s_1": 10},
        )
    ).with_multi_cloud(
        MultiCloudData(
            cloud_service_providers=["csp_1"],
            cloud_service_provider_services={"csp_1": ["s_1"]},
            min_cloud_service_provider_count=2,
            max_cloud_service_provider_count=100,
        )
    )

    Expect(model).to_be_infeasible().test()


def test_max_csp_count_constraint_infeasible():
    """Only one CSP must be used, but it's only possible with two."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1", "vm_2"],
            services=["s_1", "s_2"],
            virtual_machine_services={"vm_1": ["s_1"], "vm_2": ["s_2"]},
            service_base_costs={"s_1": 10, "s_2": 10},
        )
    ).with_multi_cloud(
        MultiCloudData(
            cloud_service_providers=["csp_1", "csp_2"],
            cloud_service_provider_services={"csp_1": ["s_1"], "csp_2": ["s_2"]},
            min_cloud_service_provider_count=0,
            max_cloud_service_provider_count=1,
        )
    )

    Expect(model).to_be_infeasible().test()
