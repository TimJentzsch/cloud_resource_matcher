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


def step_validate() -> Step:
    return (
        Step()
        .register_extension(ValidateBaseExt)
        .register_extension(ValidatePerformanceExt)
        .register_extension(ValidateNetworkExt)
        .register_extension(ValidateMultiCloudExt)
    )


def step_build_mip() -> Step:
    return (
        Step()
        .register_extension(BuildMipBaseExt)
        .register_extension(BuildMipPerformanceExt)
        .register_extension(BuildMipNetworkExt)
        .register_extension(BuildMipMultiCloudExt)
    )


def step_solve() -> Step:
    return Step().register_extension(SolveExt)


def step_extract_solution() -> Step:
    return (
        Step().register_extension(ExtractSolutionCostExt).register_extension(ExtractSolutionBaseExt)
    )
