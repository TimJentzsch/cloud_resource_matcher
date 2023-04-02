from .data import BaseData
from .validate import ValidateBaseTask
from .build_mip import BuildMipBaseTask, BaseMipData
from .extract_solution import ExtractSolutionBaseTask, BaseSolution
from optiframe.framework import OptimizationPackage

base_package = OptimizationPackage(
    validate=ValidateBaseTask, build_mip=BuildMipBaseTask, extract_solution=ExtractSolutionBaseTask
)

__all__ = ["BaseData", "BaseMipData", "BaseSolution", "base_package"]
