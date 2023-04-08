from .data import PerformanceData
from .pre_processing import PreProcessingPerformanceTask
from .validate import ValidatePerformanceTask
from .build_mip import BuildMipPerformanceTask
from optiframe.framework import OptimizationPackage

performance_package = OptimizationPackage(
    validate=ValidatePerformanceTask,
    pre_processing=PreProcessingPerformanceTask,
    build_mip=BuildMipPerformanceTask,
)

__all__ = ["PerformanceData", "performance_package"]
