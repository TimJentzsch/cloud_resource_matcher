from optimizer.extensions_v2.build_mip import (
    BuildMipBaseExt,
    BuildMipPerformanceExt,
    BuildMipNetworkExt,
    BuildMipMultiCloudExt,
)
from optimizer.extensions_v2.extract_solution import (
    ExtractSolutionCostExt,
    ExtractSolutionBaseExt,
)
from optimizer.extensions_v2.solve import SolveExt
from optimizer.extensions_v2.validate import (
    ValidateBaseExt,
    ValidatePerformanceExt,
    ValidateNetworkExt,
    ValidateMultiCloudExt,
)
from optimizer.optimizer_v2.step import Step


def step_validate(performance: bool, network: bool, multi_cloud: bool) -> Step:
    step = Step().register_extension(ValidateBaseExt)

    if performance:
        step.register_extension(ValidatePerformanceExt)
    if network:
        step.register_extension(ValidateNetworkExt)
    if multi_cloud:
        step.register_extension(ValidateMultiCloudExt)

    return step


def step_build_mip(performance: bool, network: bool, multi_cloud: bool) -> Step:
    step = Step().register_extension(BuildMipBaseExt)

    if performance:
        step.register_extension(BuildMipPerformanceExt)
    if network:
        step.register_extension(BuildMipNetworkExt)
    if multi_cloud:
        step.register_extension(BuildMipMultiCloudExt)

    return step


def step_solve() -> Step:
    return Step().register_extension(SolveExt)


def step_extract_solution() -> Step:
    return (
        Step().register_extension(ExtractSolutionCostExt).register_extension(ExtractSolutionBaseExt)
    )
