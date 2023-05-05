"""The service limits module.

This module enables the number of instances for cloud services to be restricted.
This can be helpful to represent popular regions where the servers are at capacity.
"""
from optiframe import OptimizationModule

from .data import ServiceLimitsData
from .mip_construction import MipConstructionServiceLimitsTask
from .validation import ValidationServiceLimitsTask

service_limits_module = OptimizationModule(
    validation=ValidationServiceLimitsTask, mip_construction=MipConstructionServiceLimitsTask
)

__all__ = ["ServiceLimitsData", "service_limits_module"]
