from optimizer.data import BaseData
from optimizer.workflow_engine import Task


class ValidateBaseTask(Task[None]):
    base_data: BaseData

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def execute(self) -> None:
        self.base_data.validate()
