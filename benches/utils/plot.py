"""Utility functions to plot the benchmark results."""
import matplotlib.pyplot as plt
from optiframe import ModelSize, StepData, StepTimes

from benches.utils.results import get_model_size, get_total_time

LINE_WIDTH = 3


def plot_results(variation_name: str, param_values: list[int], solutions: list[StepData]) -> None:
    """Create a line graph for the benchmark results."""
    model_sizes: list[int] = [get_model_size(solution[ModelSize]) for solution in solutions]
    optimization_times: list[float] = [
        get_total_time(solution[StepTimes]).total_seconds() for solution in solutions
    ]

    col_model_size = "black"
    col_optimization_time = "gray"

    fig, ax = plt.subplots()
    ax.set_xlabel(variation_name)

    # Model size plot
    (size_plot,) = ax.plot(
        param_values,
        model_sizes,
        label="model size",
        color=col_model_size,
        marker="o",
        linewidth=LINE_WIDTH,
    )
    ax.set_ylim(bottom=0)
    ax.set_ylabel("model size")

    # Optimization time plot
    ax2 = ax.twinx()
    (time_plot,) = ax2.plot(
        param_values,
        optimization_times,
        label="total optimization time",
        color=col_optimization_time,
        marker="v",
        linewidth=LINE_WIDTH,
    )
    ax2.set_ylim(bottom=0)
    ax2.set_ylabel("total optimization time (s)")

    # Legend
    ax.legend(handles=[size_plot, time_plot])

    # Save the plot
    fig.savefig(f"benches/output/png/{variation_name}.png")
    fig.savefig(f"benches/output/pdf/{variation_name}.pdf")
