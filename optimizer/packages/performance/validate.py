from optiframe import Task

from optimizer.packages.base import BaseData
from .data import PerformanceData


class ValidatePerformanceTask(Task[None]):
    base_data: BaseData
    performance_data: PerformanceData

    def __init__(self, base_data: BaseData, performance_data: PerformanceData):
        self.base_data = base_data
        self.performance_data = performance_data

    def execute(self) -> None:
        self.performance_data.validate(self.base_data)
