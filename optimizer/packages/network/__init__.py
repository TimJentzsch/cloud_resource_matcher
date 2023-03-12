from .validate import ValidateNetworkTask
from .build_mip import BuildMipNetworkTask, NetworkMipData
from ...framework import OptimizationPackage

NETWORK_PACKAGE = OptimizationPackage(validate=ValidateNetworkTask, build_mip=BuildMipNetworkTask)
