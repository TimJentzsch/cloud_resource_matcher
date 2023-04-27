from typing import Any

from optiframe import Optimizer
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize

from benches.utils import run_benchmark
from benches.utils.data_generation import generate_base_data
from optimizer.packages.base import base_package


DEFAULT_PARAMS = {
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
    run_benchmark(
        "cloud resource count",
        "cr_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count() -> None:
    run_benchmark(
        "cloud service count",
        "cs_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        {**DEFAULT_PARAMS, "cs_count_per_cr": 100},
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count_per_cr() -> None:
    run_benchmark(
        "count of applicable cloud services per cloud resource",
        "cs_count_per_cr",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def get_optimizer(params: dict[str, Any]) -> InitializedOptimizer:
    base_data = generate_base_data(**params)
    return Optimizer("bench_base", sense=LpMinimize).add_modules(base_package).initialize(base_data)
