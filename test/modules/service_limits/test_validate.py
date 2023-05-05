"""Tests for the validation step of the service limits module."""
import pytest

from cloud_resource_matcher.modules.base import BaseData
from cloud_resource_matcher.modules.service_limits import ServiceLimitsData
from cloud_resource_matcher.modules.service_limits.validation import ValidationServiceLimitsTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        cloud_resources=["cr_0"],
        cloud_services=["cs_0"],
        cr_to_cs_list={"cr_0": ["cs_0"]},
        cs_to_base_cost={"cs_0": 5},
        cr_to_instance_demand={"cr_0": 1},
    )

    service_limits_data = ServiceLimitsData(
        cs_to_instance_limit={"cs_0": 1}, cr_to_max_instance_demand={"cr_0": 1}
    )

    ValidationServiceLimitsTask(base_data, service_limits_data).execute()


class TestCsToInstanceLimit:
    """Tests for the cs_to_instance_limit attribute."""

    def test_should_raise_error_for_invalid_service(self) -> None:
        """One of the CSs does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": 1, "cs_1": 1},
            cr_to_max_instance_demand={"cr_0": 1},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()

    def test_should_raise_error_for_negative_instance_count(self) -> None:
        """A maximum instance count is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": -1},
            cr_to_max_instance_demand={"cr_0": 1},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()


class TestCrToMaxInstanceDemand:
    """Tests for the cr_to_max_instance_demand attribute."""

    def test_should_raise_error_for_invalid_cr(self) -> None:
        """One of the CRs does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": 1, "cs_1": 1},
            cr_to_max_instance_demand={"cr_0": 1, "cr_1": 1},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()

    def test_should_raise_error_for_negative_instance_demand(self) -> None:
        """A maximum instance demand is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": 1},
            cr_to_max_instance_demand={"cr_0": -1},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()

    def test_should_raise_error_for_max_greater_than_total(self) -> None:
        """The maximum instance demand of a CR is greater than the total demand."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": 1},
            cr_to_max_instance_demand={"cr_0": 2},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()

    def test_should_raise_error_for_missing_entry(self) -> None:
        """One CR does not have a maximum instance demand specified."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 1},
            cr_to_instance_demand={"cr_0": 1},
        )

        service_limits_data = ServiceLimitsData(
            cs_to_instance_limit={"cs_0": 1},
            cr_to_max_instance_demand={},
        )

        with pytest.raises(AssertionError):
            ValidationServiceLimitsTask(base_data, service_limits_data).execute()
