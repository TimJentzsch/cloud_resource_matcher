from dataclasses import dataclass
from typing import Dict

from optimizer.data import Service, VirtualMachine


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
