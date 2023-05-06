"""Utility functions for the benchmark tool."""
from typing import Any, Callable

from optiframe.framework import InitializedOptimizer

from benches.utils.cli import get_cli_args
from benches.utils.plot import plot_results
from benches.utils.run import run_benchmark


def setup_benchmark(
    variation_name: str,
    param_name: str,
    param_values: list[int],
    default_params: dict[str, Any],
    get_optimizer_fn: Callable[[dict[str, Any]], InitializedOptimizer],
) -> None:
    """Run a benchmark and plot the results."""
    args = get_cli_args()

    results = run_benchmark(
        variation_name,
        param_name,
        param_values,
        default_params,
        get_optimizer_fn,
        args.measures,
        args.solver,
    )

    plot_results(results)
