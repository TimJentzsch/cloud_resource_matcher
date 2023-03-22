from .validate import ValidateMultiCloudTask
from .build_mip import BuildMipMultiCloudTask, MultiCloudMipData
from optiframe.framework import OptimizationPackage

MULTI_CLOUD_PACKAGE = OptimizationPackage(
    validate=ValidateMultiCloudTask, build_mip=BuildMipMultiCloudTask
)

__all__ = ["MultiCloudMipData"]
