import pytest

from optimizer.data.base_data import BaseData


def test_should_not_raise_error_for_valid_data():
    """Validating valid data should not raise an assertion error."""
    data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
        max_service_instances={},
    )

    data.validate()


class TestValidateVirtualMachineServices:
    def test_should_raise_error_for_missing_virtual_machine(self):
        """One VM does not have the valid services defined."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_invalid_virtual_machine(self):
        """The valid services are defined for a VM that doesn't exist."""
        data = BaseData(
            virtual_machines=[],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_invalid_service(self):
        """One of the valid services for a VM does not exist."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=[],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()


class TestServiceBaseCosts:
    def test_should_raise_error_for_missing_service(self):
        """One service does not have base costs defined."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_invalid_service(self):
        """One service that has base costs defined does not exist."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=[],
            virtual_machine_services={"vm_0": []},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()


class TestVirtualMachineDemand:
    def test_should_raise_error_for_missing_entry(self):
        """A VM-time pair does not have the demand defined."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_invalid_virtual_machine(self):
        """A VM that has the demand defined does not exist."""
        data = BaseData(
            virtual_machines=[],
            services=["s_0"],
            virtual_machine_services={},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_invalid_time(self):
        """A time that has the demand defined does not exist."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()

    def test_should_raise_error_for_negative_demand(self):
        """A defined demand is negative."""
        data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): -1},
            max_service_instances={},
        )

        with pytest.raises(AssertionError):
            data.validate()
