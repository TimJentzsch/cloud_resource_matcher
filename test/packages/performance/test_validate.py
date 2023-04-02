import pytest

from optimizer.packages.base import BaseData
from optimizer.packages.performance import PerformanceData
from optimizer.packages.performance.validate import ValidatePerformanceTask


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

    performance_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM"],
        performance_demand={("vm_0", "vCPUs"): 3},
        performance_supply={("s_0", "vCPUs"): 4, ("s_0", "RAM"): 2},
    )

    ValidatePerformanceTask(base_data, performance_data).execute()


class TestValidatePerformanceDemand:
    def test_should_raise_error_for_invalid_vm(self) -> None:
        """A demand is defined for a VM that doesn't exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("vm_0", "vCPUs"): 3, ("vm_1", "vCPUs"): 2},
            performance_supply={("s_0", "vCPUs"): 4, ("s_0", "RAM"): 2},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_invalid_pc(self) -> None:
        """A demand is defined for a performance criterion that doesn't exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("vm_0", "vCPUs"): 3, ("vm_0", "apples"): 2},
            performance_supply={("s_0", "vCPUs"): 4, ("s_0", "RAM"): 2},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()


class TestValidatePerformanceSupply:
    def test_should_raise_error_for_invalid_cs(self) -> None:
        """A supply is defined for a CS that doesn't exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("vm_0", "vCPUs"): 3},
            performance_supply={("s_0", "vCPUs"): 4, ("s_0", "RAM"): 2, ("s_1", "vCPUs"): 2},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_invalid_pc(self) -> None:
        """A supply is defined for a performance criterion that doesn't exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("vm_0", "vCPUs"): 3},
            performance_supply={("s_0", "vCPUs"): 4, ("s_0", "RAM"): 2, ("s_0", "apples"): 3},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()

    def test_should_raise_error_for_missing_supply(self) -> None:
        """A supply is NOT defined for an existing CS-PC pair."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        performance_data = PerformanceData(
            performance_criteria=["vCPUs", "RAM"],
            performance_demand={("vm_0", "vCPUs"): 3},
            performance_supply={("s_0", "vCPUs"): 4},
        )

        with pytest.raises(AssertionError):
            ValidatePerformanceTask(base_data, performance_data).execute()
