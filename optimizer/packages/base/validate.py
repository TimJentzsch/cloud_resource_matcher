from .data import BaseData
from optiframe import Task


class ValidateBaseTask(Task[None]):
    base_data: BaseData

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def execute(self) -> None:
        self.base_data.validate()
