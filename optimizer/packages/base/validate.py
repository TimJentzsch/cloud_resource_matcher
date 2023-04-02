from .data import BaseData
from optiframe import Task


class ValidateBaseTask(Task[None]):
    base_data: BaseData

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def execute(self) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate virtual_machine_services
        for v in self.base_data.virtual_machines:
            assert (
                v in self.base_data.virtual_machine_services.keys()
            ), f"Valid services for VM {v} not defined"

        for v, services in self.base_data.virtual_machine_services.items():
            assert (
                v in self.base_data.virtual_machines
            ), f"{v} in virtual_machine_services is not a valid VM"
            for s in services:
                assert (
                    s in self.base_data.services
                ), f"{s} in virtual_machine_services is not a valid service"

        # Validate service_base_costs
        for s in self.base_data.services:
            assert (
                s in self.base_data.service_base_costs.keys()
            ), f"Base cost for service {s} not defined"

        for s, cost in self.base_data.service_base_costs.items():
            assert s in self.base_data.services, f"{s} in service_base_costs is not a valid service"
            assert cost >= 0, f"Cost {cost} for service {s} is negative"

        # Validate virtual_machine_demand
        for v in self.base_data.virtual_machines:
            for t in self.base_data.time:
                assert (
                    v,
                    t,
                ) in self.base_data.virtual_machine_demand.keys(), (
                    f"No demand defined for VM {v} at time {t}"
                )

        for (v, t), demand in self.base_data.virtual_machine_demand.items():
            assert (
                v in self.base_data.virtual_machines
            ), f"{v} in virtual_machine_demand is not a valid VM"
            assert t in self.base_data.time, f"{t} in virtual_machine_demand is not a valid time"
            assert demand >= 0, f"Demand {demand} for VM {v} at time {t} is negative"

        # Validate max_service_instances
        for (s, instances) in self.base_data.max_service_instances.items():
            assert (
                s in self.base_data.services
            ), f"{s} in max_service_instances is not a valid service"
            assert instances >= 0, f"Negative max instance count {instances} for service {s}"
