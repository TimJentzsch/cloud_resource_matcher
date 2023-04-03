import pytest

from optimizer.packages.base import BaseData
from optimizer.packages.multi_cloud import MultiCloudData
from optimizer.packages.multi_cloud.validate import ValidateMultiCloudTask


def test_should_not_raise_error_for_valid_data() -> None:
    """Validating valid data should not raise an assertion error."""
    base_data = BaseData(
        cloud_resources=["vm_0"],
        cloud_services=["s_0"],
        cr_to_cs_list={"vm_0": ["s_0"]},
        cs_to_base_cost={"s_0": 5},
        time=[0],
        cr_and_time_to_instance_demand={("vm_0", 0): 1},
        cs_to_instance_limit={},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=["csp_0"],
        cloud_service_provider_services={"csp_0": ["s_0"]},
        max_cloud_service_provider_count=1,
        min_cloud_service_provider_count=0,
        cloud_service_provider_costs={"csp_0": 10},
    )

    ValidateMultiCloudTask(base_data, multi_data).execute()


class TestValidateCloudServiceProviderServices:
    def test_should_raise_error_for_missing_cloud_service_provider(self) -> None:
        """One CSP is missing the definition of cloud_cloud_services that belong to it."""
        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_invalid_cloud_service_provider(self) -> None:
        """One CSP in the definitions does not exist."""
        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_invalid_service(self) -> None:
        """One service in the definitions does not exist."""
        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0", "s_1"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_for_unmatched_service(self) -> None:
        """One service has not been matched to a CSP."""
        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=[],
            cloud_service_provider_services={},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()


class TestValidateCloudServiceProviderMinMaxCounts:
    def test_should_raise_error_on_negative_min_count(self) -> None:
        """The min_cloud_service_provider_count is negative."""

        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=-1,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_on_negative_max_count(self) -> None:
        """The max_cloud_service_provider_count is negative."""

        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=-1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()

    def test_should_raise_error_on_max_smaller_min_count(self) -> None:
        """
        The max_cloud_service_provider_count is smaller than
        max_cloud_service_provider_count.
        """

        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=2,
            cloud_service_provider_costs={"csp_0": 10},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()


class TestValidateCloudServiceProviderCosts:
    def test_should_raise_error_on_missing_csp(self) -> None:
        """One of the CSPs does not have a cost defined."""
        base_data = BaseData(
            cloud_resources=["vm_0"],
            cloud_services=["s_0"],
            cr_to_cs_list={"vm_0": ["s_0"]},
            cs_to_base_cost={"s_0": 5},
            time=[0],
            cr_and_time_to_instance_demand={("vm_0", 0): 1},
            cs_to_instance_limit={},
        )

        multi_data = MultiCloudData(
            cloud_service_providers=["csp_0"],
            cloud_service_provider_services={"csp_0": ["s_0"]},
            max_cloud_service_provider_count=1,
            min_cloud_service_provider_count=0,
            cloud_service_provider_costs={},
        )

        with pytest.raises(AssertionError):
            ValidateMultiCloudTask(base_data, multi_data).execute()
