"""The multi cloud module.

This module can be used when multiple cloud service providers are considered for the deployment.
A minimum and maximum number of used CSPs can be enforced.
Migration costs for the CSPs can also be represented.
"""
from optiframe import OptimizationModule

from .data import MultiCloudData
from .mip_construction import MipConstructionMultiCloudTask, MultiCloudMipData
from .solution_extraction import MultiCloudSolution, SolutionExtractionMultiCloudTask
from .validation import ValidationMultiCloudTask

multi_cloud_module = OptimizationModule(
    validation=ValidationMultiCloudTask,
    mip_construction=MipConstructionMultiCloudTask,
    solution_extraction=SolutionExtractionMultiCloudTask,
)

__all__ = ["MultiCloudData", "MultiCloudMipData", "MultiCloudSolution", "multi_cloud_module"]
