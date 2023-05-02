"""Utility functions to format the benchmark results."""
from datetime import timedelta

from optiframe import StepData
from optiframe.framework import ModelSize, StepTimes


def print_result(instance: str, solution: StepData) -> None:
    """Print out the benchmark results in the console."""
    model_size: ModelSize = solution[ModelSize]
    step_times: StepTimes = solution[StepTimes]

    step_time_list = [
        (step_times.validate, "vd"),
        (step_times.pre_processing, "pp"),
        (step_times.build_mip, "bm"),
        (step_times.solve, "sv"),
        (step_times.extract_solution, "es"),
    ]

    total_time = sum((time for time, _ in step_time_list), timedelta())
    step_time_str = " -> ".join(f"{name} {format_time(time)}" for time, name in step_time_list)

    print(f"- {instance}")
    print(f"    model_size: {model_size.variable_count:,} x {model_size.constraint_count:,}")
    print(f"    time: {format_time(total_time)} ({step_time_str})")


def format_time(time: timedelta) -> str:
    """Format the time needed for the optimization."""
    return f"{time.total_seconds():.3f}s"
