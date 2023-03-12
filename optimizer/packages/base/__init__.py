from .validate import ValidateBaseTask
from .build_mip import BuildMipBaseTask, BaseMipData
from .extract_solution import ExtractSolutionBaseTask, BaseSolution
from optiframe.framework import OptimizationPackage

BASE_PACKAGE = OptimizationPackage(
    validate=ValidateBaseTask, build_mip=BuildMipBaseTask, extract_solution=ExtractSolutionBaseTask
)
