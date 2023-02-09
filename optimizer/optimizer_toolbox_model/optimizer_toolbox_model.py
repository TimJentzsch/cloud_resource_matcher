from dataclasses import dataclass
from typing import Self

from optimizer.optimizer_toolbox_model import BaseData, PerformanceData, NetworkData, MultiCloudData


@dataclass
class OptimizerToolboxModel:
    base_data: BaseData
    performance_data: PerformanceData | None = None
    network_data: NetworkData | None = None
    multi_cloud_data: MultiCloudData | None = None

    def __init__(self, base_data: BaseData):
        """Create a new OptimizerToolboxModel."""
        self.base_data = base_data

    def with_performance_data(self, performance_data: PerformanceData) -> Self:
        """Add performance data to the model."""
        self.performance_data = performance_data

    def with_network_data(self, network_data: NetworkData) -> Self:
        """Add network data to the model."""
        self.network_data = network_data

    def with_multi_cloud_data(self, multi_cloud_data: MultiCloudData) -> Self:
        """Add multi cloud data to the model."""
        self.multi_cloud_data = multi_cloud_data
