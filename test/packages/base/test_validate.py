import pytest

from optimizer.packages.base import BaseData
from optimizer.packages.base.validate import ValidateBaseTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    data = BaseData(
        cloud_resources=["cr_0"],
        cloud_services=["cs_0"],
        cr_to_cs_list={"cr_0": ["cs_0"]},
        cs_to_base_cost={"cs_0": 5},
        time=[0],
        cr_and_time_to_instance_demand={("cr_0", 0): 1},
    )

    ValidateBaseTask(data).execute()


class TestCrToCsList:
    def test_should_raise_error_for_missing_cr(self) -> None:
        """One CR does not have the valid CSs defined."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_cr(self) -> None:
        """The valid CSs are defined for a CR that doesn't exist."""
        data = BaseData(
            cloud_resources=[],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_service(self) -> None:
        """One of the valid CSs for a CR does not exist."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=[],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()


class TestCrToBaseCost:
    def test_should_raise_error_for_missing_cs(self) -> None:
        """One CS does not have base costs defined."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_cs(self) -> None:
        """One CS that has base costs defined does not exist."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=[],
            cr_to_cs_list={"cr_0": []},
            cs_to_base_cost={"cs_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()


class TestCrAndTimeToInstanceDemand:
    def test_should_raise_error_for_missing_entry(self) -> None:
        """A CR-time pair does not have the demand defined."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_cr(self) -> None:
        """A CR that has the demand defined does not exist."""
        data = BaseData(
            cloud_resources=[],
            cloud_services=["cs_0"],
            cr_to_cs_list={},
            cs_to_base_cost={"cs_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_invalid_time(self) -> None:
        """A time that has the demand defined does not exist."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            time=[],
            cr_and_time_to_instance_demand={("cr_0", 0): 1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()

    def test_should_raise_error_for_negative_demand(self) -> None:
        """A defined demand is negative."""
        data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            time=[0],
            cr_and_time_to_instance_demand={("cr_0", 0): -1},
        )

        with pytest.raises(AssertionError):
            ValidateBaseTask(data).execute()
