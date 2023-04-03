import pytest

from optimizer.packages.base import BaseData
from optimizer.packages.base.validate import ValidateBaseTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    data = BaseData(
        cloud_resources=["vm_0"],
        cloud_services=["s_0"],
        cr_to_cs_list={"vm_0": ["s_0"]},
        cs_to_base_cost={"s_0": 5},
        time=[0],
        cr_and_time_to_instance_demand={("vm_0", 0): 1},
        cs_to_instance_limit={"s_0": 1},
    )

    ValidateBaseTask(data).execute()


class TestValidateVirtualMachineServices:
    def test_should_raise_error_for_missing_virtual_machine(self) -> None:
        """One VM does not have the valid cloud_cloud_services defined."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_virtual_machine(self) -> None:
        """The valid cloud_cloud_services are defined for a VM that doesn't exist."""
        data = BaseData(
            cloud_resources=[],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_service(self) -> None:
        """One of the valid cloud_cloud_services for a VM does not exist."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=[],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()


class TestServiceBaseCosts:
    def test_should_raise_error_for_missing_service(self) -> None:
        """One service does not have base costs defined."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_service(self) -> None:
        """One service that has base costs defined does not exist."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=[],
            cr_to_cs_list={"vm_0": []},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()


class TestVirtualMachineDemand:
    def test_should_raise_error_for_missing_entry(self) -> None:
        """A VM-time pair does not have the demand defined."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_virtual_machine(self) -> None:
        """A VM that has the demand defined does not exist."""
        data = BaseData(
            cloud_resources=[],
            cloud_services=["s_0"],
            cr_to_cs_list={},
            cs_to_base_cost={"s_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_time(self) -> None:
        """A time that has the demand defined does not exist."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_negative_demand(self) -> None:
        """A defined demand is negative."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): -1},
            cs_to_instance_limit={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()


class TestMaxServiceInstances:
    def test_should_raise_error_for_invalid_service(self) -> None:
        """One of the cloud_cloud_services does not exist."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={"s_0": 1, "s_1": 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_negative_instance_count(self) -> None:
        """A maximum instance count is negative."""
        data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={"s_0": -1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()
