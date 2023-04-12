from optiframe.framework.tasks import ValidateTask

from optimizer.packages.base import BaseData
from .data import ServiceLimitsData


class ValidateServiceLimitsTask(ValidateTask):
    base_data: BaseData
    service_limits_data: ServiceLimitsData

    def __init__(self, base_data: BaseData, service_limits_data: ServiceLimitsData):
        self.base_data = base_data
        self.service_limits_data = service_limits_data

    def execute(self) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate cs_to_instance_limit
        for (cs, instances) in self.base_data.cs_to_instance_limit.items():
            assert (
                cs in self.base_data.cloud_services
            ), f"{cs} in cs_to_instance_limit is not a valid CS"
            assert instances >= 0, f"Negative max instance count {instances} for CS {cs}"
