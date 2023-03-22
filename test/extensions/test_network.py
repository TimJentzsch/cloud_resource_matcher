from optimizer.data import BaseData, NetworkData
from optiframe import Optimizer
from optimizer.packages import BASE_PACKAGE, NETWORK_PACKAGE
from test.framework import Expect


OPTIMIZER = Optimizer("test_network").add_package(BASE_PACKAGE).add_package(NETWORK_PACKAGE)


def test_computation_of_vm_locations() -> None:
    """Ensure that the location of a VM corresponds to the service it's placed at.

    One VM is only at one location.
    """
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            service_base_costs={"s_0": 5, "s_1": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 3, ("vm_1", 0): 4},
            max_service_instances={},
        ),
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5 for loc1 in locations for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={},
            location_traffic_cost={(loc1, loc2): 0 for loc1 in locations for loc2 in locations},
        ),
    )

    Expect(optimizer).with_fixed_vm_service_matching(
        {("vm_0", "s_0"): 1, ("vm_1", "s_1"): 1}
    ).to_be_feasible().with_variable_values(
        {
            "vm_location(vm_0,loc_0)": 1,
            "vm_location(vm_0,loc_1)": 0,
            "vm_location(vm_1,loc_0)": 0,
            "vm_location(vm_1,loc_1)": 1,
        }
    ).test()


def test_should_pay_for_vm_location_costs() -> None:
    """
    Ensure that the cost of traffic between VMs and specific locations is paid for.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 3},
            max_service_instances={},
        ),
        NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 3},
            location_traffic_cost={("loc_0", "loc_0"): 2},
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
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        ),
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_1"): 5},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_1"): 1},
            location_traffic_cost={
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
            virtual_machines=["vm_0"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0", "s_1"]},
            service_base_costs={"s_0": 5, "s_1": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        ),
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 5},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 1},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1}
    ).with_variable_values(
        {
            "vm_location(vm_0,loc_0)": 1,
            "vm_location(vm_0,loc_1)": 0,
        }
    ).test()


def test_should_calculate_connections_between_vms() -> None:
    """Two VMs are connected and need to be placed in two different locations."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            service_base_costs={"s_0": 5, "s_1": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 3},
            max_service_instances={},
        ),
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5 for loc1 in locations for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={
                ("vm_0", "vm_1"): 2,
                ("vm_1", "vm_0"): 1,
            },
            virtual_machine_location_traffic={},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_1", 0): 3}
    ).with_variable_values(
        {
            "vm_vm_locations(vm_0,vm_1,loc_0,loc_0)": 0,
            "vm_vm_locations(vm_0,vm_1,loc_0,loc_1)": 1,
            "vm_vm_locations(vm_0,vm_1,loc_1,loc_0)": 0,
            "vm_vm_locations(vm_0,vm_1,loc_1,loc_1)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_0,loc_0)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_0,loc_1)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_1,loc_0)": 1,
            "vm_vm_locations(vm_1,vm_0,loc_1,loc_1)": 0,
        }
    ).test()


def test_should_consider_latency_for_vm_vm_connections() -> None:
    """One of the connections between two VMs violates the maximum latency."""
    locations = {"loc_0", "loc_1"}

    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0", "vm_1"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
            service_base_costs={"s_0": 5, "s_1": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
            max_service_instances={},
        ),
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={("vm_0", "vm_1"): 5},
            virtual_machine_virtual_machine_traffic={
                ("vm_0", "vm_1"): 1,
            },
            virtual_machine_location_traffic={},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10 for loc1 in locations for loc2 in locations
            },
        ),
    )

    Expect(optimizer).to_be_infeasible().test()
