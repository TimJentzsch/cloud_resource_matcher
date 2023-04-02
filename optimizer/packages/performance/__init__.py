from .data import PerformanceData
from .validate import ValidatePerformanceTask
from .build_mip import BuildMipPerformanceTask
from optiframe.framework import OptimizationPackage

PERFORMANCE_PACKAGE = OptimizationPackage(
    validate=ValidatePerformanceTask, build_mip=BuildMipPerformanceTask
)

__all__ = ["PerformanceData", "PERFORMANCE_PACKAGE"]
