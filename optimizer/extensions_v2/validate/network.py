from optimizer.data import NetworkData, BaseData
from optimizer.optimizer_v2.extension import Extension


class ValidateNetworkExt(Extension[None]):
    base_data: BaseData
    network_data: NetworkData

    def __init__(self, base_data: BaseData, network_data: NetworkData):
        self.base_data = base_data
        self.network_data = network_data

    def action(self) -> None:
        self.network_data.validate(self.base_data)
