from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpVariable, LpBinary, lpSum, pulp

from .decorators import dependencies
from .extension import Extension
from .data.base_data import BaseData
from .data.types import Service, Cost, VirtualMachine, TimeUnit


VarVmServiceMatching = dict[tuple[VirtualMachine, Service], LpVariable]
VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]
ServiceVirtualMachines = dict[Service, set[VirtualMachine]]


@dataclass
class BaseMipData:
    data: BaseData
    # Which VM should be deployed on which service?
    var_vm_matching: VarVmServiceMatching
    # Which services are used at all?
    var_service_used: dict[Service, LpVariable]


@dataclass
class BaseSolution:
    """
    The most important parts of the solution, including the assignment
    of VMs to services and the total cost of the deployment.
    """
    mip_data: BaseMipData
    # Which VM should be deployed on which service?
    vm_service_matching: VmServiceMatching
    # How many instances of each service should be bought?
    service_instance_count: ServiceInstanceCount
    # What is the total cost of the deployment?
    # This also includes cost factors of other extensions.
    cost: Cost


class BaseExtension(Extension):
    """
    An extension providing basic aspects of cloud cost optimization.
    This will be needed for almost all optimization problems.

    It provides means to define the available VMs and services
    and the basic logic needed to match them together.
    """
    @staticmethod
    def identifier() -> str:
        return "base"

    @staticmethod
    @dependencies()
    def validate(data: BaseData) -> None:
        data.validate()

    @staticmethod
    @dependencies()
    def extend_mip(
        data: BaseData, problem: LpProblem, objective: LpAffineExpression
    ) -> BaseMipData:
        # Pre-compute which services can host which VMs
        service_virtual_machines: ServiceVirtualMachines = {
            s: set(
                vm
                for vm in data.virtual_machines
                if s in data.virtual_machine_services[vm]
            )
            for s in data.services
        }

        # Assign virtual machine v to cloud service s at time t?
        # ASSUMPTION: Each service instance can only be used by one VM instance
        # ASSUMPTION: All instances of one VM have to be deployed
        # on the same service type
        var_vm_matching: VarVmServiceMatching = {
            (v, s): LpVariable(f"vm_matching({v},{s})", cat=LpBinary)
            for v in data.virtual_machines
            for s in data.virtual_machine_services[v]
        }

        # Satisfy VM demands
        for vm in data.virtual_machines:
            problem += (
                lpSum(var_vm_matching[vm, s] for s in data.virtual_machine_services[vm])
                == 1,
                f"vm_demand({vm})",
            )

        # Has service s been purchased at all?
        var_service_used: dict[Service, LpVariable] = {
            s: LpVariable(f"service_used({s})", cat=LpBinary) for s in data.services
        }

        # Enforce limits for service instance count
        for s, max_instances in data.max_service_instances.items():
            for t in data.time:
                problem += (
                    lpSum(
                        var_vm_matching[vm, s] * data.virtual_machine_demand[vm, t]
                        for vm in service_virtual_machines[s]
                    )
                    <= max_instances,
                    f"max_service_instances({s},{t})",
                )

        # Calculate service_used
        for s in data.services:
            for t in data.time:
                problem += (
                    var_service_used[s]
                    <= lpSum(
                        var_vm_matching[vm, s] for vm in service_virtual_machines[s]
                    ),
                    f"connect_service_instances_and_service_used({s},{t})",
                )

        # Base costs for used services
        objective += lpSum(
            var_vm_matching[vm, s]
            * data.virtual_machine_demand[vm, t]
            * data.service_base_costs[s]
            for vm in data.virtual_machines
            for s in data.virtual_machine_services[vm]
            for t in data.time
        )

        return BaseMipData(
            data=data,
            var_vm_matching=var_vm_matching,
            var_service_used=var_service_used,
        )

    @staticmethod
    @dependencies()
    def extract_solution(mip_data: BaseMipData, problem: LpProblem) -> BaseSolution:
        base_data = mip_data.data
        vm_service_matching: VmServiceMatching = dict()

        for v in base_data.virtual_machines:
            for s in base_data.virtual_machine_services[v]:
                for t in base_data.time:
                    value = (
                        round(pulp.value(mip_data.var_vm_matching[v, s]))
                        * base_data.virtual_machine_demand[v, t]
                    )

                    if value >= 1:
                        vm_service_matching[v, s, t] = value

        service_instance_count: ServiceInstanceCount = {}

        for s in base_data.services:
            for t in base_data.time:
                value = sum(
                    round(pulp.value(mip_data.var_vm_matching[vm, s]))
                    * base_data.virtual_machine_demand[vm, t]
                    for vm in base_data.virtual_machines
                    if s in base_data.virtual_machine_services[vm]
                )

                if value >= 1:
                    service_instance_count[s, t] = value

        cost = problem.objective.value()

        return BaseSolution(
            mip_data=mip_data,
            vm_service_matching=vm_service_matching,
            service_instance_count=service_instance_count,
            cost=cost,
        )
