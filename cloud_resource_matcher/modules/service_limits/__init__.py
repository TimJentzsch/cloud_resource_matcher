"""The service limits module.

This module enables the number of instances for cloud services to be restricted.
This can be helpful to represent popular regions where the servers are at capacity.
"""
from optiframe.framework import OptimizationModule

from .build_mip import BuildMipServiceLimitsTask
from .data import ServiceLimitsData
from .validate import ValidateServiceLimitsTask

service_limits_module = OptimizationModule(
    validate=ValidateServiceLimitsTask, build_mip=BuildMipServiceLimitsTask
)

__all__ = ["ServiceLimitsData", "service_limits_module"]
