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


def bench() -> None:
    params: BenchParams = {"cr_count": 1, "cs_count": 1, "cs_count_per_cr": 1}
    bench_instance(params)

    print("\n-----\n")

    params: BenchParams = {"cr_count": 3, "cs_count": 7, "cs_count_per_cr": 5}
    bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)

    try:
        solution = optimizer.print_mip_and_solve(PULP_CBC_CMD(msg=False))
        print_result(f"{params}", solution)
    except InfeasibleError:
        print(f"- {params}  INFEASIBLE")


def get_optimizer(params: BenchParams) -> InitializedOptimizer:
    base_data = generate_base_data(**params)
    return Optimizer("bench_base", sense=LpMinimize).add_package(base_package).initialize(base_data)
