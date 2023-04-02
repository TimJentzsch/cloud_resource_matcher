from .data import PerformanceData
from .validate import ValidatePerformanceTask
from .build_mip import BuildMipPerformanceTask
from optiframe.framework import OptimizationPackage

performance_package = OptimizationPackage(
    validate=ValidatePerformanceTask, build_mip=BuildMipPerformanceTask
)

__all__ = ["PerformanceData", "performance_package"]
