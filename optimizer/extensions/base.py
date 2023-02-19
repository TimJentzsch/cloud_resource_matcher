from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression, LpVariable, LpBinary, lpSum, pulp

from .decorators import dependencies
from .extension import Extension
from optimizer.mixed_integer_program.types import (
    ServiceVirtualMachines,
    VarVmServiceMatching,
    VmServiceMatching, ServiceInstanceCount,
)
from optimizer.optimizer_toolbox_model import BaseData
from optimizer.optimizer_toolbox_model.data import Service, Cost


@dataclass
class BaseMipData:
    data: BaseData
    var_vm_matching: VarVmServiceMatching
    var_service_used: dict[Service, LpVariable]


@dataclass
class BaseSolution:
    mip_data: BaseMipData
    vm_service_matching: VmServiceMatching
    service_instance_count: ServiceInstanceCount
    cost: Cost


class BaseExtension(Extension):
    @staticmethod
    def identifier() -> str:
        return "base"

    @dependencies()
    def validate(self, data: BaseData) -> None:
        data.validate()

    @dependencies()
    def extend_mip(
        self, data: BaseData, problem: LpProblem, objective: LpAffineExpression
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

    @dependencies()
    def extract_solution(self, mip_data: BaseMipData, problem: LpProblem) -> BaseSolution:
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
            cost=cost
        )
