from optimizer.extensions.decorators import validate_dependencies
from optimizer.optimizer_toolbox_model import BaseData


class BaseExtension:
    @staticmethod
    def identifier() -> str:
        return "base"

    @validate_dependencies()
    def validate(self, data: BaseData) -> None:
        data.validate()

    def extend_mip(self):
        pass
