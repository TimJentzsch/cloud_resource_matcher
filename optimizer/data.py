from typing import List, Dict, Tuple
from dataclasses import dataclass


Service = str
CloudServiceProvider = str
Region = str
VirtualMachine = str
Cost = float
TimeUnit = int


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

    def validate(self):
        """Validate the data for consistency."""
        # Validate virtual_machine_services
        for v in self.virtual_machines:
            assert (
                v in self.virtual_machine_services.keys()
            ), f"Valid services for VM {v} not defined"

        for v, services in self.virtual_machine_services.items():
            assert (
                v in self.virtual_machines
            ), f"{v} in virtual_machine_services is not a valid VM"
            for s in services:
                assert (
                    s in self.services
                ), f"{s} in virtual_machine_services is not a valid service"

        # Validate service_base_costs
        for s in self.services:
            assert (
                s in self.service_base_costs.keys()
            ), f"Base cost for service {s} not defined"

        for s, cost in self.service_base_costs.items():
            assert (
                s in self.services
            ), f"{s} in service_base_costs is not a valid service"
            assert cost >= 0, f"Cost {cost} for service {s} is negative"

        # Validate virtual_machine_demand
        for v in self.virtual_machines:
            for t in self.time:
                assert (
                    v,
                    t,
                ) in self.virtual_machine_demand.keys(), (
                    f"No demand defined for VM {v} at time {t}"
                )

        for (v, t), demand in self.virtual_machine_demand.items():
            assert (
                v in self.virtual_machines
            ), f"{v} in virtual_machine_demand is not a valid VM"
            assert t in self.time, f"{t} in virtual_machine_demand is not a valid time"
            assert demand >= 0, f"Demand {demand} for VM {v} at time {t} is negative"


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
