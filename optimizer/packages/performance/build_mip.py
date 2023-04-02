from pulp import LpProblem

from optimizer.packages.base import BaseData, BaseMipData
from optiframe import Task

from .data import PerformanceData


class BuildMipPerformanceTask(Task[None]):
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

    def execute(self) -> None:
        # Enforce performance limits for every cloud service
        for (vm, pc), demand in self.performance_data.performance_demand.items():
            for cs in self.base_data.virtual_machine_services[vm]:
                if supply := self.performance_data.performance_supply.get((cs, pc)):
                    if supply < demand:
                        self.problem += (
                            self.base_mip_data.var_vm_matching[vm, cs] == 0,
                            f"performance_limit({vm},{cs},{pc})",
                        )
