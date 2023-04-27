from .data import ServiceLimitsData
from .validate import ValidateServiceLimitsTask
from .build_mip import BuildMipServiceLimitsTask
from optiframe.framework import OptimizationModule

service_limits_package = OptimizationModule(
    validate=ValidateServiceLimitsTask, build_mip=BuildMipServiceLimitsTask
)

__all__ = ["ServiceLimitsData", "service_limits_package"]
