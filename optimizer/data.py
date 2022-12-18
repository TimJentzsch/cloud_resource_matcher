from typing import List, Dict
from dataclasses import dataclass


Service = str
CloudServiceProvider = str
Region = str
VirtualMachine = str
Cost = float


@dataclass
class BaseData:
    # The available virtual machines
    virtual_machines: List[VirtualMachine]

    # The available services
    services: List[Service]

    # The services that are applicable for each virtual machine
    virtual_machine_services: Dict[VirtualMachine, Service]

    # The base cost for each service
    service_base_costs: Dict[Service, Cost]


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


@dataclass
class MultiCloudData:
    # The available cloud service providers
    cloud_service_providers: List[CloudServiceProvider]

    # The services each cloud service provider offers
    cloud_service_provider_services: Dict[CloudServiceProvider, List[Service]]

    # The minimum number of cloud service providers that have to be used
    min_cloud_service_provider_count: int

    # The maximum number of cloud service providers that can be used
    max_cloud_service_provider_count: int
