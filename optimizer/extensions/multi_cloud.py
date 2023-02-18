from optimizer.optimizer_toolbox_model import BaseData
from optimizer.extensions.decorators import dependencies
from optimizer.optimizer_toolbox_model import MultiCloudData


class PerformanceExtension:
    @staticmethod
    def identifier() -> str:
        return "multi_cloud"

    @dependencies("base")
    def validate(self, data: MultiCloudData, base: BaseData):
        data.validate(base)

    def extend_mip(self):
        pass
