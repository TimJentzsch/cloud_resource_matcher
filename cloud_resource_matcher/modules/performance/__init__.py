"""The performance module.

This module can be used to enforce performance requirements
and to represent usage-based pricing models.
"""
from optiframe.framework import OptimizationModule

from .build_mip import BuildMipPerformanceTask
from .data import PerformanceData
from .pre_processing import PreProcessingPerformanceTask
from .validate import ValidatePerformanceTask

performance_module = OptimizationModule(
    validate=ValidatePerformanceTask,
    pre_processing=PreProcessingPerformanceTask,
    build_mip=BuildMipPerformanceTask,
)

__all__ = ["PerformanceData", "performance_module"]
