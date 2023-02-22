from dataclasses import dataclass
from typing import Dict

from optimizer.extensions.data.types import Service, VirtualMachine
from optimizer.extensions.data.base_data import BaseData


@dataclass
class PerformanceData:
    # The minimum amount of RAM each virtual machine requires
    virtual_machine_min_ram: Dict[VirtualMachine, int]

    # The minimum mount of vCPUs each virtual machine requires
    virtual_machine_min_cpu_count: Dict[VirtualMachine, int]

    # The amount of RAM each service has
    service_ram: Dict[Service, int]

    # The amount of vCPUs each service has
    service_cpu_count: Dict[Service, int]

    def validate(self, base_data: BaseData) -> None:
        """
        Validate the data for consistency.

        :raises AssertionError: When the data is not valid.
        """
        # Validate virtual_machine_min_ram
        for v, min_ram in self.virtual_machine_min_ram.items():
            assert (
                v in base_data.virtual_machines
            ), f"{v} in virtual_machine_min_ram is not a valid VM"
            assert min_ram >= 0, f"Min RAM for VM {v} cannot be negative"

        # Validate virtual_machine_min_cpu_count
        for v, cpu_count in self.virtual_machine_min_cpu_count.items():
            assert (
                v in base_data.virtual_machines
            ), f"{v} in virtual_machine_min_cpu_count is not a valid VM"
            assert cpu_count >= 0, f"Min RAM for VM {v} cannot be negative"

        # Validate service_ram
        for s in base_data.services:
            assert s in self.service_ram.keys(), f"No RAM defined for service {s}"

        for s, ram in self.service_ram.items():
            assert s in base_data.services, f"{s} in service_ram is not a valid service"
            assert ram >= 0, f"RAM for service {s} cannot be negative"

        # Validate service_cpu_count
        for s in base_data.services:
            assert (
                s in self.service_cpu_count.keys()
            ), f"No CPU count defined for service {s}"

        for s, cpu_count in self.service_cpu_count.items():
            assert s in base_data.services, f"{s} in service_ram is not a valid service"
            assert cpu_count >= 0, f"RAM for service {s} cannot be negative"
