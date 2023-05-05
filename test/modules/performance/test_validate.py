"""Tests for the validation step of the performance module."""
import pytest

from cloud_resource_matcher.modules.base import BaseData
from cloud_resource_matcher.modules.performance import PerformanceData
from cloud_resource_matcher.modules.performance.validation import ValidatePerformanceTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        cloud_resources=["cr_0"],
        cloud_services=["cs_0"],
        cr_to_cs_list={"cr_0": ["cs_0"]},
        cs_to_base_cost={"cs_0": 5},
        cr_to_instance_demand={"cr_0": 1},
    )

    performance_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM"],
        performance_demand={("cr_0", "vCPUs"): 3},
        performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2},
        cost_per_unit={("cs_0", "RAM"): 3},
    )

    ValidatePerformanceTask(base_data, performance_data).execute()


class TestValidatePerformanceDemand:
    """Tests for the performance_demand attribute."""

    def test_should_raise_error_for_invalid_vm(self) -> None:
        """A demand is defined for a VM that doesn't exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3, ("cr_1", "vCPUs"): 2},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2},
            cost_per_unit={("cs_0", "RAM"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_invalid_pc(self) -> None:
        """A demand is defined for a performance criterion that doesn't exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3, ("cr_0", "apples"): 2},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2},
            cost_per_unit={("cs_0", "RAM"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()


class TestValidatePerformanceSupply:
    """Tests for the performance_supply attribute."""

    def test_should_raise_error_for_invalid_cs(self) -> None:
        """A supply is defined for a CS that doesn't exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2, ("cs_1", "vCPUs"): 2},
            cost_per_unit={("cs_0", "RAM"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_invalid_pc(self) -> None:
        """A supply is defined for a performance criterion that doesn't exist."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2, ("cs_0", "apples"): 3},
            cost_per_unit={("cs_0", "RAM"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_missing_supply(self) -> None:
        """A supply is NOT defined for an existing CS-PC pair."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3},
            performance_supply={("cs_0", "vCPUs"): 4},
            cost_per_unit={("cs_0", "RAM"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()


class TestValidateCostPerUnit:
    """Tests for the cost_per_unit attribute."""

    def test_should_raise_error_for_invalid_cs(self) -> None:
        """Should raise error if an invalid CS is specified in the cost."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2},
            cost_per_unit={("cs_0", "RAM"): 3, ("cs_1", "RAM"): 2},
        )

        with pytest.raises(AssertionError, match="cs_1 in cost_per_unit is not a valid CS"):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_invalid_pc(self) -> None:
        """Should raise error if an invalid perf. criterion is specified in the cost."""
        base_data = BaseData(
            cloud_resources=["cr_0"],
            cloud_services=["cs_0"],
            cr_to_cs_list={"cr_0": ["cs_0"]},
            cs_to_base_cost={"cs_0": 5},
            cr_to_instance_demand={"cr_0": 1},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("cr_0", "vCPUs"): 3},
            performance_supply={("cs_0", "vCPUs"): 4, ("cs_0", "RAM"): 2},
            cost_per_unit={("cs_0", "RAM"): 3, ("cs_0", "apples"): 2},
        )

        with pytest.raises(
            AssertionError, match="apples in cost_per_unit is not a valid performance criterion"
        ):
            ValidatePerformanceTask(base_data, performance_data).execute()
