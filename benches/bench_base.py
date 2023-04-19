from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result, generate_base_data
from optimizer.packages.base import BaseData, base_package


class BenchParams(TypedDict):
    cr_count: int
    cs_count: int
    cs_count_per_cr: int


DEFAULT_PARAMS: BenchParams = {
    "cr_count": 1000,
    "cs_count": 1000,
    "cs_count_per_cr": 1000,
}


def bench() -> None:
    print("=== CR_COUNT ===")
    bench_cr_count()

    print("\n\n=== CS_COUNT ===")
    bench_cs_count()

    print("\n\n=== CS_COUNT_PER_CR ===")
    bench_cs_count_per_cr()


def bench_cr_count() -> None:
    cr_counts = [10, 25, 50, 100, 200, 500, 1000]

    for cr_count in cr_counts:
        params: BenchParams = {**DEFAULT_PARAMS, "cr_count": cr_count}  # type: ignore
        bench_instance(params)


def bench_cs_count() -> None:
    cs_counts = [10, 25, 50, 100, 200, 500, 1000]

    for cs_count in cs_counts:
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cs_count": cs_count,
            "cs_count_per_cr": cs_count,
        }
        bench_instance(params)


def bench_cs_count_per_cr() -> None:
    cs_count_per_crs = [10, 25, 50, 100, 200, 500, 1000]

    for cs_count_per_cr in cs_count_per_crs:
        params: BenchParams = {**DEFAULT_PARAMS, "cs_count_per_cr": cs_count_per_cr}  # type: ignore
        bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)

    try:
        solution = optimizer.solve(PULP_CBC_CMD(msg=False))
        print_result(f"{params}", solution)
    except InfeasibleError:
        print(f"- {params}  INFEASIBLE")


def get_optimizer(params: BenchParams) -> InitializedOptimizer:
    base_data = generate_base_data(**params)
    return Optimizer("bench_base", sense=LpMinimize).add_package(base_package).initialize(base_data)
