"""Utilities to run a benchmark."""
from dataclasses import dataclass
from typing import Any, Callable

from optiframe import InfeasibleError, ModelSize, StepTimes
from optiframe.framework import InitializedOptimizer

from .formatting import print_result


@dataclass
class BenchmarkTime:
    """The times need to optimize the problem instance, in seconds."""

    total: float
    validation: float
    pre_processing: float
    mip_construction: float
    solving: float
    solution_extraction: float


@dataclass
class BenchmarkMeasure:
    """The benchmark measures for a single parameter value."""

    param_value: int
    times: list[BenchmarkTime]
    variable_count: int
    constraint_count: int


@dataclass
class BenchmarkResult:
    """The result of a benchmark suite."""

    variation_name: str
    param_name: str
    param_values: list[int]
    default_params: dict[str, Any]
    measures: list[BenchmarkMeasure]


def run_benchmark(
    variation_name: str,
    param_name: str,
    param_values: list[int],
    default_params: dict[str, Any],
    get_optimizer_fn: Callable[[dict[str, Any]], InitializedOptimizer],
    measure_count: int,
    solver: Any,
) -> BenchmarkResult:
    """Run the given benchmark and return the result."""
    measures: list[BenchmarkMeasure] = list()

    for val in param_values:
        variable_count: int = 0
        constraint_count: int = 0
        times: list[BenchmarkTime] = list()

        for _ in range(measure_count):
            params = {**default_params, param_name: val}
            optimizer = get_optimizer_fn(params)

            try:
                solution = optimizer.solve(solver=solver)
                print_result(f"{params}", solution)

                model_size: ModelSize = solution[ModelSize]
                variable_count = model_size.variable_count
                constraint_count = model_size.constraint_count

                step_times: StepTimes = solution[StepTimes]
                times.append(
                    BenchmarkTime(
                        total=step_times.total.total_seconds(),
                        validation=step_times.validate.total_seconds(),
                        pre_processing=step_times.pre_processing.total_seconds(),
                        mip_construction=step_times.build_mip.total_seconds(),
                        solving=step_times.solve.total_seconds(),
                        solution_extraction=step_times.extract_solution.total_seconds(),
                    )
                )
            except InfeasibleError:
                print(f"- {params}  INFEASIBLE")

        measures.append(
            BenchmarkMeasure(
                param_value=val,
                variable_count=variable_count,
                constraint_count=constraint_count,
                times=times,
            )
        )

    return BenchmarkResult(
        variation_name=variation_name,
        param_name=param_name,
        param_values=param_values,
        default_params=default_params,
        measures=measures,
    )
