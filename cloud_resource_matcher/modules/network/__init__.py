"""The network module.

This module can be used to represent network connections,
enforce maximum latency requirements and specify network usage costs.
"""
from optiframe import OptimizationModule

from .data import NetworkData
from .mip_construction import MipConstructionNetworkTask, NetworkMipData
from .pre_processing import PreProcessingNetworkTask
from .validation import ValidateNetworkTask

network_module = OptimizationModule(
    validation=ValidateNetworkTask,
    pre_processing=PreProcessingNetworkTask,
    mip_construction=MipConstructionNetworkTask,
)

__all__ = ["NetworkData", "NetworkMipData", "network_module"]
