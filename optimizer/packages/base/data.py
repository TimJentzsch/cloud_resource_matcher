from dataclasses import dataclass
from typing import List, Dict, Tuple


Service = str
VirtualMachine = str
TimeUnit = int
Cost = float


@dataclass
class BaseData:
    # The available virtual machines
    virtual_machines: List[VirtualMachine]

    # The available services
    services: List[Service]

    # The services that are applicable for each virtual machine
    virtual_machine_services: Dict[VirtualMachine, List[Service]]

    # The base cost for each service
    service_base_costs: Dict[Service, Cost]

    # The discrete units of time when a decision can be made
    time: List[TimeUnit]

    # The number of virtual machine instances that are needed at a given point in time
    virtual_machine_demand: Dict[Tuple[VirtualMachine, TimeUnit], int]

    # The maximum number of instances available for each service
    max_service_instances: Dict[Service, int]
