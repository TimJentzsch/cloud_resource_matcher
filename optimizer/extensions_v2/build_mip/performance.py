from pulp import LpProblem

from optimizer.data import BaseData, PerformanceData
from .base import BaseMipData
from optimizer.optimizer_v2.extension import Extension


class BuildMipPerformanceExt(Extension[None]):
    base_data: BaseData
    performance_data: PerformanceData
    base_mip_data: BaseMipData
    problem: LpProblem

    def __init__(
        self,
        base_data: BaseData,
        performance_data: PerformanceData,
        base_mip_data: BaseMipData,
        problem: LpProblem,
    ):
        self.base_data = base_data
        self.performance_data = performance_data
        self.base_mip_data = base_mip_data
        self.problem = problem

    def action(self) -> None:
        # Enforce performance limits for every service
        for vm in self.base_data.virtual_machines:
            for s in self.base_data.virtual_machine_services[vm]:
                if vm in self.performance_data.virtual_machine_min_ram.keys():
                    # RAM
                    self.problem += (
                        self.base_mip_data.var_vm_matching[vm, s]
                        * self.performance_data.virtual_machine_min_ram[vm]
                        <= self.performance_data.service_ram[s],
                        f"ram_performance_limit({vm},{s})",
                    )

                if vm in self.performance_data.virtual_machine_min_cpu_count.keys():
                    # vCPUs
                    self.problem += (
                        self.base_mip_data.var_vm_matching[vm, s]
                        * self.performance_data.virtual_machine_min_cpu_count[vm]
                        <= self.performance_data.service_cpu_count[s],
                        f"cpu_performance_limit({vm},{s})",
                    )
