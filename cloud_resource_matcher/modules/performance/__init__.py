"""The performance module.

This module can be used to enforce performance requirements
and to represent usage-based pricing models.
"""
from optiframe import OptimizationModule

from .mip_construction import MipConstructionPerformanceTask
from .data import PerformanceData
from .pre_processing import PreProcessingPerformanceTask
from .validation import ValidatePerformanceTask

performance_module = OptimizationModule(
    validation=ValidatePerformanceTask,
    pre_processing=PreProcessingPerformanceTask,
    mip_construction=MipConstructionPerformanceTask,
)

__all__ = ["PerformanceData", "performance_module"]
