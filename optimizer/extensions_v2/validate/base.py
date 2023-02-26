from optimizer.data import BaseData
from optimizer.optimizer_v2.extension import Extension


class ValidateBaseExt(Extension[None]):
    base_data: BaseData

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def action(self) -> None:
        self.base_data.validate()
