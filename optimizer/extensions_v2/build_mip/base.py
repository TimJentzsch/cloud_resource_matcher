from dataclasses import dataclass

from pulp import LpVariable, LpProblem, LpAffineExpression, LpBinary, lpSum

from optimizer.data import BaseData
from optimizer.data.types import VirtualMachine, Service, TimeUnit
from optimizer.optimizer_v2.extension import Extension


VarVmServiceMatching = dict[tuple[VirtualMachine, Service], LpVariable]
VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]
ServiceVirtualMachines = dict[Service, set[VirtualMachine]]


@dataclass
class BaseMipData:
    # Which VM should be deployed on which service?
    var_vm_matching: VarVmServiceMatching
    # Which services are used at all?
    var_service_used: dict[Service, LpVariable]


class BuildMipBaseExt(Extension[BaseMipData]):
    base_data: BaseData
    problem: LpProblem
    objective: LpAffineExpression

    def __init__(
        self, base_data: BaseData, problem: LpProblem, objective: LpAffineExpression
    ):
        self.base_data = base_data
        self.problem = problem
        self.objective = objective

    def action(self) -> BaseMipData:
        # Pre-compute which services can host which VMs
        service_virtual_machines: ServiceVirtualMachines = {
            s: set(
                vm
                for vm in self.base_data.virtual_machines
                if s in self.base_data.virtual_machine_services[vm]
            )
            for s in self.base_data.services
        }

        # Assign virtual machine v to cloud service s at time t?
        # ASSUMPTION: Each service instance can only be used by one VM instance
        # ASSUMPTION: All instances of one VM have to be deployed
        # on the same service type
        var_vm_matching: VarVmServiceMatching = {
            (v, s): LpVariable(f"vm_matching({v},{s})", cat=LpBinary)
            for v in self.base_data.virtual_machines
            for s in self.base_data.virtual_machine_services[v]
        }

        # Satisfy VM demands
        for vm in self.base_data.virtual_machines:
            self.problem += (
                lpSum(
                    var_vm_matching[vm, s]
                    for s in self.base_data.virtual_machine_services[vm]
                )
                == 1,
                f"vm_demand({vm})",
            )

        # Has service s been purchased at all?
        var_service_used: dict[Service, LpVariable] = {
            s: LpVariable(f"service_used({s})", cat=LpBinary)
            for s in self.base_data.services
        }

        # Enforce limits for service instance count
        for s, max_instances in self.base_data.max_service_instances.items():
            for t in self.base_data.time:
                self.problem += (
                    lpSum(
                        var_vm_matching[vm, s]
                        * self.base_data.virtual_machine_demand[vm, t]
                        for vm in service_virtual_machines[s]
                    )
                    <= max_instances,
                    f"max_service_instances({s},{t})",
                )

        # Calculate service_used
        for s in self.base_data.services:
            for t in self.base_data.time:
                self.problem += (
                    var_service_used[s]
                    <= lpSum(
                        var_vm_matching[vm, s] for vm in service_virtual_machines[s]
                    ),
                    f"connect_service_instances_and_service_used({s},{t})",
                )

        # Base costs for used services
        self.objective += lpSum(
            var_vm_matching[vm, s]
            * self.base_data.virtual_machine_demand[vm, t]
            * self.base_data.service_base_costs[s]
            for vm in self.base_data.virtual_machines
            for s in self.base_data.virtual_machine_services[vm]
            for t in self.base_data.time
        )

        return BaseMipData(
            var_vm_matching=var_vm_matching,
            var_service_used=var_service_used,
        )
