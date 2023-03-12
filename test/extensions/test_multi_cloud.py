from optimizer.data import BaseData, MultiCloudData
from optiframe import Optimizer
from optimizer.packages import BASE_PACKAGE, MULTI_CLOUD_PACKAGE
from test.framework import Expect


OPTIMIZER = Optimizer("test_multi_cloud").add_package(BASE_PACKAGE).add_package(MULTI_CLOUD_PACKAGE)


def test_min_csp_count_constraint_matching():
    """There are two CSPs, one cheap and one expensive.
    To respect the min CSP count constraint, both CSPs have to be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1", "s_2"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1", "s_2"]},
            service_base_costs={"s_0": 1, "s_1": 1, "s_2": 10},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
            max_service_instances={},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            cloud_service_provider_services={
                "csp_0": ["s_0", "s_1"],
                "csp_1": ["s_2"],
            },
            min_cloud_service_provider_count=2,
            max_cloud_service_provider_count=100,
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(11).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_2", 0): 1}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 1}).test()


def test_max_csp_count_constraint_matching():
    """There are two CSPs, it would be cheapest to use most of them.
    To respect the max CSP count constraint, only one CSP can be used.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1", "s_2"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1", "s_2"]},
            service_base_costs={"s_0": 10, "s_1": 10, "s_2": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
            max_service_instances={},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            cloud_service_provider_services={
                "csp_0": ["s_0", "s_1"],
                "csp_1": ["s_2"],
            },
            min_cloud_service_provider_count=0,
            max_cloud_service_provider_count=1,
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(20).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_1", 0): 1}
    ).with_variable_values({"csp_used(csp_0)": 1, "csp_used(csp_1)": 0}).test()


def test_min_csp_count_constraint_infeasible():
    """Two CSPs have to be used, but there is only one CSP."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 10},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            min_cloud_service_provider_count=2,
            max_cloud_service_provider_count=100,
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_max_csp_count_constraint_infeasible():
    """Only one CSP must be used, but it's only possible with two."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            service_base_costs={"s_0": 10, "s_1": 10},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
            max_service_instances={},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0", "csp_1"],
            cloud_service_provider_services={"csp_0": ["s_0"], "csp_1": ["s_1"]},
            min_cloud_service_provider_count=0,
            max_cloud_service_provider_count=1,
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_with_multiple_time_points():
    """Make sure that the CSP constraints also work for multiple time points."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 10},
            time=[0, 1],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_0", 1): 1},
            max_service_instances={},
        ),
        MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            min_cloud_service_provider_count=1,
            max_cloud_service_provider_count=1,
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_0", "s_0", 1): 1}
    ).with_cost(20).test()
