from optiframe import Task

from optimizer.packages.base import BaseData
from .data import NetworkData


class ValidateNetworkTask(Task[None]):
    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def execute(self) -> None:
        self.network_data.validate(self.base_data)
