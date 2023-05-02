"""The network module.

This module can be used to represent network connections,
enforce maximum latency requirements and specify network usage costs.
"""
from optiframe.framework import OptimizationModule

from .build_mip import BuildMipNetworkTask, NetworkMipData
from .data import NetworkData
from .pre_processing import PreProcessingNetworkTask
from .validate import ValidateNetworkTask

network_module = OptimizationModule(
    validate=ValidateNetworkTask,
    pre_processing=PreProcessingNetworkTask,
    build_mip=BuildMipNetworkTask,
)

__all__ = ["NetworkData", "NetworkMipData", "network_module"]
