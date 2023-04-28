"""Tests for the validation step of the network module."""
import pytest

from optimizer.modules.base import BaseData
from optimizer.modules.network import NetworkData
from optimizer.modules.network.validate import ValidateNetworkTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        cloud_resources=["cr_0"],
        cloud_services=["cs_0"],
        cr_to_cs_list={"cr_0": ["cs_0"]},
        cs_to_base_cost={"cs_0": 5},
        cr_to_instance_demand={"cr_0": 1},
    )

    network_data = NetworkData(
        locations={"loc_0"},
        loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
        cs_to_loc={"cs_0": "loc_0"},
        cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
        cr_and_cr_to_traffic={},
        cr_and_cr_to_max_latency={},
        cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
        loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
    )

    ValidateNetworkTask(base_data, network_data).execute()


class TestLocAndLocToLatency:
    """Tests for the loc_and_loc_to_latency attribute."""

    def test_should_raise_error_for_missing_location_pair(self) -> None:
        """One location pair does not have a latency defined between them."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_for_invalid_location(self) -> None:
        """One location in the definitions does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0, ("loc_0", "loc_1"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_for_negative_latency(self) -> None:
        """One location pair has a negative latency."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): -1},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()


class TestCsToLoc:
    """Tests for the cs_to_loc attribute."""

    def test_should_raise_error_on_missing_service(self) -> None:
        """One cloud service has no location defined."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_service(self) -> None:
        """The max_csp_count is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0", "cs_1": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
        """A specified location does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_1"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()


class TestCrAndLocToMaxLatency:
    """Tests for the cr_and_loc_to_max_latency attribute."""

    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
        """One cloud resource does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_1", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
        """One location does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_1"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_latency(self) -> None:
        """One of the maximum latencies is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): -1},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()


class TestCrAndLocToTraffic:
    """Tests for cr_and_loc_to_traffic attribute."""

    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
        """One cloud resource does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={
                ("cr_0", "loc_0"): 10,
                ("cr_1", "loc_0"): 5,
            },
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_invalid_location(self) -> None:
        """One location does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={
                ("cr_0", "loc_0"): 10,
                ("cr_0", "loc_1"): 3,
            },
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_traffic(self) -> None:
        """One of the traffics is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): -1},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()


class TestCrAndCrToTraffic:
    """Tests for the cr_and_cr_to_traffic attribute."""

    def test_should_raise_error_on_invalid_virtual_machine(self) -> None:
        """One cloud resource does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={("cr_0", "cr_1"): 5},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_negative_traffic(self) -> None:
        """One location does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={("cr_0", "cr_0"): -1},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()


class TestLocAndLocToCost:
    """Tests for the loc_and_loc_to_cost attribute."""

    def test_should_raise_error_on_invalid_location(self) -> None:
        """One location does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={("cr_0", "loc_0"): 10},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={("loc_0", "loc_0"): 0, ("loc_0", "loc_1"): 3},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()

    def test_should_raise_error_on_missing_location_pair(self) -> None:
        """One location pair has no costs defined."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        network_data = NetworkData(
            locations={"loc_0"},
            loc_and_loc_to_latency={("loc_0", "loc_0"): 0},
            cs_to_loc={"cs_0": "loc_0"},
            cr_and_loc_to_max_latency={},
            cr_and_cr_to_max_latency={},
            cr_and_cr_to_traffic={},
            cr_and_loc_to_traffic={("cr_0", "loc_0"): 10},
            loc_and_loc_to_cost={},
        )

        with pytest.raises(AssertionError):
            ValidateNetworkTask(base_data, network_data).execute()
