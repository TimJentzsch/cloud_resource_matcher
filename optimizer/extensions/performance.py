from optimizer.optimizer_toolbox_model import BaseData
from optimizer.extensions.decorators import validate_dependencies
from optimizer.optimizer_toolbox_model import PerformanceData


class PerformanceExtension:
    @staticmethod
    def identifier() -> str:
        return "performance"

    @validate_dependencies("base")
    def validate(self, data: PerformanceData, base: BaseData):
        data.validate(base)

    def extend_mip(self):
        pass
