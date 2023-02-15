from dataclasses import dataclass
from typing import Self

from optimizer.optimizer_toolbox_model.data.base_data import BaseData
from optimizer.optimizer_toolbox_model.data.multi_cloud_data import MultiCloudData
from optimizer.optimizer_toolbox_model.data.network_data import NetworkData
from optimizer.optimizer_toolbox_model.data.performance_data import PerformanceData


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
        return self

    def with_network_data(self, network_data: NetworkData) -> Self:
        """Add network data to the model."""
        self.network_data = network_data
        return self

    def with_multi_cloud_data(self, multi_cloud_data: MultiCloudData) -> Self:
        """Add multi cloud data to the model."""
        self.multi_cloud_data = multi_cloud_data
        return self

    def validate(self) -> "ValidatedOptimizerToolboxModel":
        """
        Validate the model for integrity.

        :raises AssertionError: When the given data is not valid.
        """
        self.base_data.validate()

        if self.performance_data is not None:
            self.performance_data.validate(self.base_data)
        if self.network_data is not None:
            self.network_data.validate(self.base_data)
        if self.performance_data is not None:
            self.performance_data.validate(self.base_data)
        if self.multi_cloud_data is not None:
            self.multi_cloud_data.validate(self.base_data)

        return ValidatedOptimizerToolboxModel(self)


@dataclass
class ValidatedOptimizerToolboxModel:
    """An optimizer toolbox model that has been validated for integrity."""

    optimizer_toolbox_model: OptimizerToolboxModel

    def __init__(self, optimizer_toolbox_model: OptimizerToolboxModel):
        """
        Create a new validated optimizer toolbox model.

        This should never be created directly, unless the data has been verified at
        another place.
        Instead, call the `.validate` function on the model.
        """
        self.optimizer_toolbox_model = optimizer_toolbox_model

    def optimize(self) -> Self:
        """
        Optimize the model by applying pre-processing techniques.

        If optimizations can be applied, this will result in faster solving times
        for the model.
        """
        # FIXME: Apply optimizations
        return self
