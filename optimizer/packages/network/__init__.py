from .data import NetworkData
from .pre_processing import PreProcessingNetworkTask
from .validate import ValidateNetworkTask
from .build_mip import BuildMipNetworkTask, NetworkMipData
from optiframe.framework import OptimizationPackage

network_package = OptimizationPackage(
    validate=ValidateNetworkTask,
    pre_processing=PreProcessingNetworkTask,
    build_mip=BuildMipNetworkTask,
)

__all__ = ["NetworkData", "NetworkMipData", "network_package"]
