"""Utility functions for the benchmark tool."""
from typing import Any, Callable

from optiframe import InfeasibleError, StepData
from optiframe.framework import InitializedOptimizer

from benches.utils.cli import get_solver_from_args
from benches.utils.formatting import print_result
from benches.utils.plot import plot_results


def run_benchmark(
    variation_name: str,
    param_name: str,
    param_values: list[int],
    default_params: dict[str, Any],
    get_optimizer_fn: Callable[[dict[str, Any]], InitializedOptimizer],
) -> None:
    """Run a benchmark and plot the results."""
    solutions: list[StepData] = list()

    for val in param_values:
        params = {**default_params, param_name: val}
        optimizer = get_optimizer_fn(params)
        solver = get_solver_from_args()

        try:
            solution = optimizer.solve(solver=solver)
            print_result(f"{params}", solution)
            solutions.append(solution)
        except InfeasibleError:
            print(f"- {params}  INFEASIBLE")

    plot_results(variation_name, param_values, solutions)
