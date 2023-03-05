from .validate import ValidatePerformanceTask
from .build_mip import BuildMipPerformanceTask
from ...framework import OptimizationPackage

PerformancePackage = OptimizationPackage(
    validate=ValidatePerformanceTask, build_mip=BuildMipPerformanceTask
)
