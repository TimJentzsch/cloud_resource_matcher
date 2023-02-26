from optimizer.data import PerformanceData, BaseData
from optimizer.optimizer_v2.extension import Extension


class ValidatePerformanceExt(Extension[None]):
    base_data: BaseData
    performance_data: PerformanceData

    def __init__(self, base_data: BaseData, performance_data: PerformanceData):
        self.base_data = base_data
        self.performance_data = performance_data

    def action(self) -> None:
        self.performance_data.validate(self.base_data)
