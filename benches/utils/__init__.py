"""Utility functions for the benchmark tool."""
import json
import os
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

    # Create directories if they don't exist
    os.makedirs("benches/output/pdf", exist_ok=True)
    os.makedirs("benches/output/png", exist_ok=True)
    os.makedirs("benches/output/svg", exist_ok=True)
    os.makedirs("benches/output/json", exist_ok=True)

    if args.use_cache:
        with open(f"benches/output/json/{param_name}.json", "r") as file:
            results = json.load(file)
    else:
        results = run_benchmark(
            variation_name,
            param_name,
            param_values,
            default_params,
            get_optimizer_fn,
            args.measures,
            args.solver,
        )
        with open(f"benches/output/json/{param_name}.json", "w+") as file:
            json.dump(results, file, indent=2)

    plot_results(results, dark_theme=args.dark_theme)
