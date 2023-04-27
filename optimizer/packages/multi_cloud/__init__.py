from .data import MultiCloudData
from .validate import ValidateMultiCloudTask
from .build_mip import BuildMipMultiCloudTask, MultiCloudMipData
from optiframe.framework import OptimizationModule

multi_cloud_package = OptimizationModule(
    validate=ValidateMultiCloudTask, build_mip=BuildMipMultiCloudTask
)

__all__ = ["MultiCloudData", "MultiCloudMipData", "multi_cloud_package"]
