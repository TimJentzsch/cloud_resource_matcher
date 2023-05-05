"""The base module.

This module implements the core of the cloud resource matching problem.
It allows you to specify which cloud resources need to be deployed
and which cloud services are available.

This module isn't very useful on its own, but provides the basis for all other modules.
"""
from optiframe import OptimizationModule

from .data import BaseData
from .mip_construction import BaseMipData, MipConstructionBaseTask
from .solution_extraction import BaseSolution, SolutionExtractionBaseTask
from .validation import ValidationBaseTask

base_module = OptimizationModule(
    validation=ValidationBaseTask,
    mip_construction=MipConstructionBaseTask,
    solution_extraction=SolutionExtractionBaseTask,
)

__all__ = ["BaseData", "BaseMipData", "BaseSolution", "base_module"]
