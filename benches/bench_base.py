"""Benchmarks for the base module."""
from typing import Any

from optiframe import Optimizer
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize

from benches.utils import run_benchmark
from benches.utils.data_generation import generate_base_data
from cloud_resource_matcher.modules.base import base_module

DEFAULT_PARAMS = {
    "cr_count": 1000,
    "cs_count": 1000,
    "cs_count_per_cr": 1000,
}


def bench() -> None:
    """Run the benchmarks for the base module."""
    print("=== CR_COUNT ===")
    bench_cr_count()

    print("\n\n=== CS_COUNT ===")
    bench_cs_count()

    print("\n\n=== CS_COUNT_PER_CR ===")
    bench_cs_count_per_cr()


def bench_cr_count() -> None:
    """Run benchmarks varying the number of cloud resources."""
    run_benchmark(
        "cloud resource count",
        "cr_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count() -> None:
    """Run benchmarks varying the number of cloud services."""
    run_benchmark(
        "cloud service count",
        "cs_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        {**DEFAULT_PARAMS, "cs_count_per_cr": 100},
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count_per_cr() -> None:
    """Run benchmarks varying the number of CSs applicable for each CR."""
    run_benchmark(
        "count of applicable cloud services per cloud resource",
        "cs_count_per_cr",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def get_optimizer(params: dict[str, Any]) -> InitializedOptimizer:
    """Get an optimizer instance for the given parameters."""
    base_data = generate_base_data(**params)
    return Optimizer("bench_base", sense=LpMinimize).add_modules(base_module).initialize(base_data)
