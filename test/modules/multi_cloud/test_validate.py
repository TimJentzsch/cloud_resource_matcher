"""Tests for the validation step of the multi cloud module."""
import pytest

from optimizer.modules.base import BaseData
from optimizer.modules.multi_cloud import MultiCloudData
from optimizer.modules.multi_cloud.validate import ValidateMultiCloudTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        cloud_resources=["cr_0"],
        cloud_services=["cs_0"],
        cr_to_cs_list={"cr_0": ["cs_0"]},
        cs_to_base_cost={"cs_0": 5},
        cr_to_instance_demand={"cr_0": 1},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=["csp_0"],
        csp_to_cs_list={"csp_0": ["cs_0"]},
        max_csp_count=1,
        min_csp_count=0,
        csp_to_cost={"csp_0": 10},
    )

    ValidateMultiCloudTask(base_data, multi_data).execute()


class TestCspToCsList:
    """Tests for the csp_to_cs_list attribute."""

    def test_should_raise_error_for_missing_csp(self) -> None:
        """One CSP is missing the definition of CS that belong to it."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={},
            max_csp_count=1,
            min_csp_count=0,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_invalid_csp(self) -> None:
        """One CSP in the definitions does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            max_csp_count=1,
            min_csp_count=0,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_invalid_cs(self) -> None:
        """One CS in the definitions does not exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0", "cs_1"]},
            max_csp_count=1,
            min_csp_count=0,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_unmatched_cs(self) -> None:
        """One CS has not been matched to a CSP."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            csp_to_cs_list={},
            max_csp_count=1,
            min_csp_count=0,
            csp_to_cost={},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()


class TestMinMaxCspCount:
    """Tests for the min_csp_count and max_csp_count attributes."""

    def test_should_raise_error_on_negative_min_count(self) -> None:
        """The min_csp_count is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            max_csp_count=1,
            min_csp_count=-1,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_on_negative_max_count(self) -> None:
        """The max_csp_count is negative."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            max_csp_count=-1,
            min_csp_count=0,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_on_max_smaller_min_count(self) -> None:
        """The max_csp_count is smaller than min_csp_count."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            max_csp_count=1,
            min_csp_count=2,
            csp_to_cost={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()


class TestCspToCost:
    """Tests for the csp_to_cost attribute."""

    def test_should_raise_error_on_missing_csp(self) -> None:
        """One of the CSPs does not have a cost defined."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            csp_to_cs_list={"csp_0": ["cs_0"]},
            max_csp_count=1,
            min_csp_count=0,
            csp_to_cost={},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()
