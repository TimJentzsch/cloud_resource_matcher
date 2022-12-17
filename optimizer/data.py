from typing import List, Dict
from dataclasses import dataclass


Service = str
CloudServiceProvider = str
Region = str
VirtualMachine = str
Cost = float


@dataclass
class Data:
    virtual_machines: List[VirtualMachine]
    virtual_machine_min_ram: Dict[Service, int]
    virtual_machine_min_cpu_count: Dict[Service, int]

    regions: List[Region]

    services: List[Service]
    service_regions: Dict[Service, Region]
    service_cloud_service_providers: Dict[Service, CloudServiceProvider]
    service_base_costs: Dict[Service, Cost]
    service_ram: Dict[Service, int]
    service_cpu_count: Dict[Service, int]
