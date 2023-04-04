from optiframe import Optimizer

from optimizer.packages.base import BaseData, base_package
from optimizer.packages.network import NetworkData, network_package
from test.framework import Expect


OPTIMIZER = Optimizer("test_network").add_package(base_package).add_package(network_package)


def test_should_pay_for_vm_location_costs() -> None:
    """
    Ensure that the cost of traffic between VMs and specific locations is paid for.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 3},
            cs_to_instance_limit={},
        ),
        NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"s_0": "loc_0"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("vm_0", "loc_0"): 3},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 2},
        ),
    )

    # Make sure the network costs are included in the total costs
    # demand * service base cost + demand * traffic * traffic cost
    Expect(optimizer).to_be_feasible().with_cost(3 * 5 + 3 * 3 * 2).test()


def test_should_be_infeasible_if_max_latency_is_violated() -> None:
    """
    The virtual machine can only be placed in a location where the max latency
    can't be respected.
    """
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"s_0": "loc_0"},
            cr_and_loc_to_max_latency={("vm_0", "loc_1"): 5},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("vm_0", "loc_1"): 1},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_should_choose_matching_that_respects_max_latency() -> None:
    """The VM can be placed in two locations, but only one has low enough latency."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0", "s_1"],
            cr_to_cs_list={"vm_0": ["s_0", "s_1"]},
            cs_to_base_cost={"s_0": 5, "s_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"s_0": "loc_0", "s_1": "loc_1"},
            cr_and_loc_to_max_latency={("vm_0", "loc_0"): 5},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("vm_0", "loc_0"): 1},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching({("vm_0", "s_0", 0): 1}).test()


def test_should_calculate_service_deployments_for_vm_pairs() -> None:
    """Two VMs are connected and need to be placed on two different cloud_cloud_services."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0", "vm_1"],
            cloud_services=["s_0", "s_1"],
            cr_to_cs_list={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            cs_to_base_cost={"s_0": 5, "s_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1, ("vm_1", 0): 3},
            cs_to_instance_limit={},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"s_0": "loc_0", "s_1": "loc_1"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={
                ("vm_0", "vm_1"): 2,
                ("vm_1", "vm_0"): 1,
            },
            cr_and_loc_to_traffic={},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_1", 0): 3}
    ).with_variable_values(
        {
            "vm_pair_services(vm_0,s_0,vm_1,s_1)": 1,
            "vm_pair_services(vm_1,s_1,vm_0,s_0)": 1,
        }
    ).test()


def test_should_consider_latency_for_vm_vm_connections() -> None:
    """One of the connections between two VMs violates the maximum latency."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["vm_0", "vm_1"],
            cloud_services=["s_0", "s_1"],
            cr_to_cs_list={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            cs_to_base_cost={"s_0": 5, "s_1": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
            cs_to_instance_limit={},
        ),
        NetworkData(
            locations=locations,
            loc_and_loc_to_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            cs_to_loc={"s_0": "loc_0", "s_1": "loc_1"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={("vm_0", "vm_1"): 5},
            cr_and_cr_to_traffic={
                ("vm_0", "vm_1"): 1,
            },
            cr_and_loc_to_traffic={},
            loc_and_loc_to_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_infeasible().test()
