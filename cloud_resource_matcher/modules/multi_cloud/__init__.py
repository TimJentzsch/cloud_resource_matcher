"""The multi cloud module.

This module can be used when multiple cloud service providers are considered for the deployment.
A minimum and maximum number of used CSPs can be enforced.
Migration costs for the CSPs can also be represented.
"""
from optiframe.framework import OptimizationModule

from .build_mip import BuildMipMultiCloudTask, MultiCloudMipData
from .data import MultiCloudData
from .validate import ValidateMultiCloudTask

multi_cloud_module = OptimizationModule(
    validate=ValidateMultiCloudTask, build_mip=BuildMipMultiCloudTask
)

__all__ = ["MultiCloudData", "MultiCloudMipData", "multi_cloud_module"]
