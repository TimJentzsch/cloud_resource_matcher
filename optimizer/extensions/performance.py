from dataclasses import dataclass

from pulp import LpProblem, LpAffineExpression

from .base import BaseMipData
from .extension import Extension, ExtensionId
from .data import BaseData, PerformanceData
from optimizer.extensions.decorators import dependencies


@dataclass
class PerformanceMipData:
    data: PerformanceData


@dataclass
class PerformanceSolutionData:
    mip_data: PerformanceMipData


class PerformanceExtension(Extension):
    """
    An extension to specify performance requirements.

    It allows you to define how much performance every VM needs
    and how much performance the cloud services provide.
    """

    @staticmethod
    def identifier() -> ExtensionId:
        return "performance"

    @staticmethod
    @dependencies("base")
    def validate(data: PerformanceData, base: BaseData):
        data.validate(base)

    @staticmethod
    @dependencies("base")
    def extend_mip(
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
                        base.var_vm_matching[vm, s] * data.virtual_machine_min_cpu_count[vm]
                        <= data.service_cpu_count[s],
                        f"cpu_performance_limit({vm},{s})",
                    )

        return PerformanceMipData(data=data)

    @staticmethod
    @dependencies()
    def extract_solution(
        mip_data: PerformanceMipData, problem: LpProblem
    ) -> PerformanceSolutionData:
        return PerformanceSolutionData(mip_data)
