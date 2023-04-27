from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize

from benches.utils.cli import get_solver_from_args
from benches.utils.data_generation import generate_base_data
from benches.utils.formatting import print_result
from optimizer.modules.base import base_module


class BenchParams(TypedDict):
    cr_count: int
    cs_count: int
    cs_count_per_cr: int


def bench() -> None:
    params: BenchParams = {"cr_count": 1, "cs_count": 1, "cs_count_per_cr": 1}
    bench_instance(params)

    print("\n-----\n")

    params = {"cr_count": 3, "cs_count": 7, "cs_count_per_cr": 5}
    bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)
    solver = get_solver_from_args()

    try:
        solution = optimizer.print_mip_and_solve(solver=solver)
        print_result(f"{params}", solution)
    except InfeasibleError:
        print(f"- {params}  INFEASIBLE")


def get_optimizer(params: BenchParams) -> InitializedOptimizer:
    base_data = generate_base_data(**params)
    return Optimizer("bench_base", sense=LpMinimize).add_modules(base_module).initialize(base_data)
