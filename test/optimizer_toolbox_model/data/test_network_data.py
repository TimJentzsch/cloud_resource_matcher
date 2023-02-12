import pytest

from optimizer.optimizer_toolbox_model.data.base_data import BaseData
from optimizer.optimizer_toolbox_model.data.network_data import NetworkData


def test_should_not_raise_error_for_valid_data():
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
        max_service_instances={},
    )

    network_data = NetworkData(
        locations={"loc_0"},
        location_latency={("loc_0", "loc_0"): 0},
        service_location={"s_0": "loc_0"},
        virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
        virtual_machine_virtual_machine_traffic={},
        virtual_machine_virtual_machine_max_latency={},
        virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
        location_traffic_cost={("loc_0", "loc_0"): 0},
    )

    network_data.validate(base_data)


class TestValidateLocationLatency:
    def test_should_raise_error_for_missing_location_pair(self):
        """One location pair does not have a latency defined between them."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_for_invalid_location(self):
        """One location in the definitions does not exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0, ("loc_0", "loc_1"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_for_negative_latency(self):
        """One location pair has a negative latency."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): -1},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)


class TestValidateServiceLocation:
    def test_should_raise_error_on_missing_service(self):
        """One service has no location defined."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_invalid_service(self):
        """The max_cloud_service_provider_count is negative."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0", "s_1": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_invalid_location(self):
        """A specified location does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_1"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)


class TestValidateVirtualMachineMaxLatency:
    def test_should_raise_error_on_invalid_virtual_machine(self):
        """One virtual machine does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_1", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_invalid_location(self):
        """One location does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_1"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_negative_latency(self):
        """One of the maximum latencies is negative."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): -1},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)


class TestValidateVirtualMachineLocationTraffic:
    def test_should_raise_error_on_invalid_virtual_machine(self):
        """One virtual machine does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={
                ("vm_0", "loc_0"): 10,
                ("vm_1", "loc_0"): 5,
            },
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_invalid_location(self):
        """One location does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={
                ("vm_0", "loc_0"): 10,
                ("vm_0", "loc_1"): 3,
            },
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_negative_traffic(self):
        """One of the traffics is negative."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): -1},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)


class TestValidateVirtualMachineVirtualMachineTraffic:
    def test_should_raise_error_on_invalid_virtual_machine(self):
        """One virtual machine does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={("vm_0", "vm_1"): 5},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_negative_traffic(self):
        """One location does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={("vm_0", "vm_0"): -1},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)


class TestValidateLocationTrafficCost:
    def test_should_raise_error_on_invalid_location(self):
        """One location does not exist."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={("vm_0", "loc_0"): 10},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={("loc_0", "loc_0"): 0, ("loc_0", "loc_1"): 3},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)

    def test_should_raise_error_on_missing_location_pair(self):
        """One location pair has no costs defined."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            location_latency={("loc_0", "loc_0"): 0},
            service_location={"s_0": "loc_0"},
            virtual_machine_location_max_latency={},
            virtual_machine_virtual_machine_max_latency={},
            virtual_machine_virtual_machine_traffic={},
            virtual_machine_location_traffic={("vm_0", "loc_0"): 10},
            location_traffic_cost={},
        )

        with pytest.raises(AssertionError):
            network_data.validate(base_data)
