from optimizer.data.base_data import BaseData
from optimizer.data.network_data import NetworkData
from optimizer.model import Model
from test.framework import Expect


def test_computation_of_vm_locations():
    """Ensure that the location of a VM corresponds to the service it's placed at.

    One VM is only at one location.
    """
    base_data = BaseData(
        virtual_machines=["vm_0", "vm_1"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
        service_base_costs={"s_0": 5, "s_1": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 3, ("vm_1", 0): 4},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5
                for loc1 in locations
                for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={},
            location_traffic_cost={
                (loc1, loc2): 0 for loc1 in locations for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).with_fixed_vm_service_matching(
        {("vm_0", "s_0", 0): 3, ("vm_1", "s_1", 0): 4}
    ).to_be_feasible().with_variable_values(
        {
            "vm_location(vm_0,loc_0,0)": 3,
            "vm_location(vm_0,loc_1,0)": 0,
            "vm_location(vm_1,loc_0,0)": 0,
            "vm_location(vm_1,loc_1,0)": 4,
        }
    ).test()


def test_computation_of_vm_locations_split():
    """Ensure that the location of a VM corresponds to the service it's placed at.

    The instances of the VMs are split among multiple locations.
    """
    base_data = BaseData(
        virtual_machines=["vm_0", "vm_1"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0", "s_1"], "vm_1": ["s_0", "s_1"]},
        service_base_costs={"s_0": 5, "s_1": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 3, ("vm_1", 0): 4},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5
                for loc1 in locations
                for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={},
            location_traffic_cost={
                (loc1, loc2): 0 for loc1 in locations for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).with_fixed_vm_service_matching(
        {
            ("vm_0", "s_0", 0): 1,
            ("vm_0", "s_1", 0): 2,
            ("vm_1", "s_0", 0): 2,
            ("vm_1", "s_1", 0): 2,
        }
    ).to_be_feasible().with_variable_values(
        {
            "vm_location(vm_0,loc_0,0)": 1,
            "vm_location(vm_0,loc_1,0)": 2,
            "vm_location(vm_1,loc_0,0)": 2,
            "vm_location(vm_1,loc_1,0)": 2,
        }
    ).test()


def test_should_pay_for_vm_location_costs():
    """Ensure that the cost of traffic between VMs and specific locations is paid for."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 3},
        max_service_instances={},
    )

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 3},
            location_traffic_cost={("loc_0", "loc_0"): 2},
        ).validate(base_data)
    )

    # Make sure the network costs are included in the total costs
    # service base cost + demand * traffic * traffic cost
    Expect(model).to_be_feasible().with_cost(5 + 3 * 3 * 2).test()


def test_should_be_infeasible_if_max_latency_is_violated():
    """The virtual machine can only be placed in a location where the max latency can't be respected."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_1"): 5},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_1"): 1},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).to_be_infeasible().test()


def test_should_choose_matching_that_respects_max_latency():
    """The VM can be placed in two locations, but only one has low enough latency."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0", "s_1"]},
        service_base_costs={"s_0": 5, "s_1": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 5},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 1},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1}
    ).with_variable_values(
        {
            "vm_location(vm_0,loc_0,0)": 1,
            "vm_location(vm_0,loc_1,0)": 0,
        }
    ).test()


def test_should_calculate_connections_between_vms():
    """Two VMs are connected and need to be placed in two different locations."""
    base_data = BaseData(
        virtual_machines=["vm_0", "vm_1"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
        service_base_costs={"s_0": 5, "s_1": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 3},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 5
                for loc1 in locations
                for loc2 in locations
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
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_1", 0): 3}
    ).with_variable_values(
        {
            "vm_vm_locations(vm_0,vm_1,loc_0,loc_0,0)": 0,
            "vm_vm_locations(vm_0,vm_1,loc_0,loc_1,0)": 1,
            "vm_vm_locations(vm_0,vm_1,loc_1,loc_0,0)": 0,
            "vm_vm_locations(vm_0,vm_1,loc_1,loc_1,0)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_0,loc_0,0)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_0,loc_1,0)": 0,
            "vm_vm_locations(vm_1,vm_0,loc_1,loc_0,0)": 3,
            "vm_vm_locations(vm_1,vm_0,loc_1,loc_1,0)": 0,
        }
    ).test()


def test_should_consider_latency_for_vm_vm_connections():
    """One of the connections between two VMs violates the maximum latency."""
    base_data = BaseData(
        virtual_machines=["vm_0", "vm_1"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_1"]},
        service_base_costs={"s_0": 5, "s_1": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
        max_service_instances={},
    )

    locations = {"loc_0", "loc_1"}

    model = Model(base_data.validate()).with_network(
        NetworkData(
            locations=locations,
            location_latency={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
            service_location={"s_0": "loc_0", "s_1": "loc_1"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={("vm_0", "vm_1"): 5},
            virtual_machine_virtual_machine_traffic={
                ("vm_0", "vm_1"): 1,
            },
            virtual_machine_location_traffic={},
            location_traffic_cost={
                (loc1, loc2): 0 if loc1 == loc2 else 10
                for loc1 in locations
                for loc2 in locations
            },
        ).validate(base_data)
    )

    Expect(model).to_be_infeasible().test()
