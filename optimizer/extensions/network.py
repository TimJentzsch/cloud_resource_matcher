from optimizer.optimizer_toolbox_model import BaseData
from optimizer.extensions.decorators import validate_dependencies
from optimizer.optimizer_toolbox_model import NetworkData


class NetworkExtension:
    @staticmethod
    def identifier() -> str:
        return "network"

    @validate_dependencies("base")
    def validate(self, data: NetworkData, base: BaseData):
        data.validate(base)

    def extend_mip(self):
        pass
