import pytest

from optimizer.packages.base import BaseData
from optimizer.packages.network import NetworkData
from optimizer.packages.network.validate import ValidateNetworkTask


def test_should_not_raise_error_for_valid_data() -> None:
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

    ValidateNetworkTask(base_data, network_data).execute()


class TestValidateLocationLatency:
    def test_should_raise_error_for_missing_location_pair(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_for_invalid_location(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_for_negative_latency(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()


class TestValidateServiceLocation:
    def test_should_raise_error_on_missing_service(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_service(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()


class TestValidateVirtualMachineMaxLatency:
    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_latency(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()


class TestValidateVirtualMachineLocationTraffic:
    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_traffic(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()


class TestValidateVirtualMachineVirtualMachineTraffic:
    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_traffic(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()


class TestValidateLocationTrafficCost:
    def test_should_raise_error_on_invalid_location(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_missing_location_pair(self) -> None:
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
            ValidateNetworkTask(base_data, network_data).execute()
