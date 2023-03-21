from optimizer.data import MultiCloudData, BaseData
from optiframe import Task


class ValidateMultiCloudTask(Task[None]):
    base_data: BaseData
    multi_cloud_data: MultiCloudData

    def __init__(self, base_data: BaseData, multi_cloud_data: MultiCloudData):
        self.base_data = base_data
        self.multi_cloud_data = multi_cloud_data

    def execute(self) -> None:
        self.multi_cloud_data.validate(self.base_data)
