from .validate import ValidateNetworkTask
from .build_mip import BuildMipNetworkTask, NetworkMipData
from optiframe.framework import OptimizationPackage

NETWORK_PACKAGE = OptimizationPackage(validate=ValidateNetworkTask, build_mip=BuildMipNetworkTask)

__all__ = ["NetworkMipData"]
