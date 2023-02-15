import pytest

from optimizer.optimizer_toolbox_model.data.base_data import BaseData
from optimizer.optimizer_toolbox_model.data.multi_cloud_data import MultiCloudData


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

    multi_data = MultiCloudData(
        cloud_service_providers=["csp_0"],
        cloud_service_provider_services={"csp_0": ["s_0"]},
        max_cloud_service_provider_count=1,
        min_cloud_service_provider_count=0,
    )

    multi_data.validate(base_data)


class TestValidateCloudServiceProviderServices:
    def test_should_raise_error_for_missing_cloud_service_provider(self):
        """One CSP is missing the definition of services that belong to it."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)

    def test_should_raise_error_for_invalid_cloud_service_provider(self):
        """One CSP in the definitions does not exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)

    def test_should_raise_error_for_invalid_service(self):
        """One service in the definitions does not exist."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0", "s_1"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)

    def test_should_raise_error_for_unmatched_service(self):
        """One service has not been matched to a CSP."""
        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            cloud_service_provider_services={},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)


class TestValidateCloudServiceProviderMinMaxCounts:
    def test_should_raise_error_on_negative_min_count(self):
        """The min_cloud_service_provider_count is negative."""

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=-1,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)

    def test_should_raise_error_on_negative_max_count(self):
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

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=-1,
            min_cloud_service_provider_count=0,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)

    def test_should_raise_error_on_max_smaller_min_count(self):
        """
        The max_cloud_service_provider_count is smaller than
        max_cloud_service_provider_count.
        """

        base_data = BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=2,
        )

        with pytest.raises(AssertionError):
            multi_data.validate(base_data)
