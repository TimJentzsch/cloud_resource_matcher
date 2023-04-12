from .data import ServiceLimitsData
from .validate import ValidateServiceLimitsTask
from .build_mip import BuildMipServiceLimitsTask
from optiframe.framework import OptimizationPackage

service_limits_package = OptimizationPackage(
    validate=ValidateServiceLimitsTask, build_mip=BuildMipServiceLimitsTask
)

__all__ = ["ServiceLimitsData", "service_limits_package"]
