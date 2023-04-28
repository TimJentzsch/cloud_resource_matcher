"""The base module.

This module implements the core of the cloud resource matching problem.
It allows you to specify which cloud resources need to be deployed
and which cloud services are available.

This module isn't very useful on its own, but provides the basis for all other modules.
"""
from .data import BaseData
from .validate import ValidateBaseTask
from .build_mip import BuildMipBaseTask, BaseMipData
from .extract_solution import ExtractSolutionBaseTask, BaseSolution
from optiframe.framework import OptimizationModule

base_module = OptimizationModule(
    validate=ValidateBaseTask, build_mip=BuildMipBaseTask, extract_solution=ExtractSolutionBaseTask
)

__all__ = ["BaseData", "BaseMipData", "BaseSolution", "base_module"]
