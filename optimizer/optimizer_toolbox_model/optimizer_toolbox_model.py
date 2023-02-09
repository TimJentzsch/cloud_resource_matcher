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

    def validate(self) -> "ValidatedOptimizerToolboxModel":
        """Validate the model for integrity."""
        # FIXME: Apply validation
        return ValidatedOptimizerToolboxModel(self)


@dataclass
class ValidatedOptimizerToolboxModel:
    """An optimizer toolbox model that has been validated for integrity."""
    optimizer_toolbox_model: OptimizerToolboxModel

    def __init__(self, optimizer_toolbox_model: OptimizerToolboxModel):
        """
        Create a new validated optimizer toolbox model.

        This should never be created directly, unless the data has been verified at another place.
        Instead, call the `.validate` function on the model.
        """
        self.optimizer_toolbox_model = optimizer_toolbox_model

    def optimize(self) -> Self:
        """
        Optimize the model by applying pre-processing techniques.

        If optimizations can be applied, this will result in faster solving times for the model.
        """
        # FIXME: Apply optimizations
        return self
