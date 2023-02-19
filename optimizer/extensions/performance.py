from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression

from .base import BaseMipData
from .extension import Extension, ExtensionId
from optimizer.optimizer_toolbox_model import BaseData
from optimizer.extensions.decorators import dependencies
from optimizer.optimizer_toolbox_model import PerformanceData


@dataclass
class PerformanceMipData:
    data: PerformanceData


@dataclass
class PerformanceSolutionData:
    mip_data: PerformanceMipData


class PerformanceExtension(Extension):
    @staticmethod
    def identifier() -> ExtensionId:
        return "performance"

    @dependencies("base")
    def validate(self, data: PerformanceData, base: BaseData):
        data.validate(base)

    @dependencies("base")
    def extend_mip(
        self,
        data: PerformanceData,
        problem: LpProblem,
        objective: LpAffineExpression,
        base: BaseMipData,
    ) -> PerformanceMipData:
        # Enforce performance limits for every service
        for vm in base.data.virtual_machines:
            for s in base.data.virtual_machine_services[vm]:
                if vm in data.virtual_machine_min_ram.keys():
                    # RAM
                    problem += (
                        base.var_vm_matching[vm, s] * data.virtual_machine_min_ram[vm]
                        <= data.service_ram[s],
                        f"ram_performance_limit({vm},{s})",
                    )

                if vm in data.virtual_machine_min_cpu_count.keys():
                    # vCPUs
                    problem += (
                        base.var_vm_matching[vm, s]
                        * data.virtual_machine_min_cpu_count[vm]
                        <= data.service_cpu_count[s],
                        f"cpu_performance_limit({vm},{s})",
                    )

        return PerformanceMipData(data=data)

    @dependencies()
    def extract_solution(self, mip_data: PerformanceMipData) -> PerformanceSolutionData:
        return PerformanceSolutionData(mip_data)
