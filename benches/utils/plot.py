"""Utility functions to plot the benchmark results."""
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from benches.utils.run import BenchmarkResult

LINE_WIDTH = 3


def plot_results(result: BenchmarkResult, dark_theme: bool = False) -> None:
    """Create a line graph for the benchmark results."""
    model_sizes: list[int] = [
        measure["variable_count"] * measure["constraint_count"] for measure in result["measures"]
    ]
    # Take the average of all measurements
    optimization_times: list[float] = [
        sum(time["total"] for time in measure["times"]) / len(measure["times"])
        for measure in result["measures"]
    ]

    # Colors
    col_background = "#121212" if dark_theme else "white"
    col_text = "white" if dark_theme else "black"
    col_lines = col_text
    col_model_size = "#93bce1" if dark_theme else "black"
    col_optimization_time = "#b993e1" if dark_theme else "gray"

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()
    ax.set_xlabel(result["variation_name"], color=col_text)

    # Model size plot
    (size_plot,) = ax.plot(
        result["param_values"],
        model_sizes,
        label="model size",
        color=col_model_size,
        marker="o",
        linewidth=LINE_WIDTH,
    )
    ax.set_ylim(bottom=0)
    ax.set_ylabel("model size", color=col_text)

    ax.patch.set_facecolor(col_background)
    ax.xaxis.set_tick_params(color=col_lines, labelcolor=col_lines)
    ax.yaxis.set_tick_params(color=col_lines, labelcolor=col_lines)

    for spine in ax.spines.values():
        spine.set_edgecolor(col_lines)

    # Optimization time plot
    ax2: Axes = ax.twinx()
    (time_plot,) = ax2.plot(
        result["param_values"],
        optimization_times,
        label="total optimization time",
        color=col_optimization_time,
        marker="v",
        linewidth=LINE_WIDTH,
    )
    ax2.set_ylim(bottom=0)
    ax2.set_ylabel("total optimization time (s)", color=col_text)

    ax2.patch.set_facecolor(col_background)
    ax2.xaxis.set_tick_params(color=col_lines, labelcolor=col_lines)
    ax2.yaxis.set_tick_params(color=col_lines, labelcolor=col_lines)

    for spine in ax2.spines.values():
        spine.set_edgecolor(col_lines)

    # Legend
    ax.legend(
        handles=[size_plot, time_plot],
        labelcolor=col_text,
        edgecolor=col_lines,
        facecolor=col_background,
    )

    fig.patch.set_facecolor(col_background)

    # Save the plot
    fig.savefig(f"benches/output/png/{result['param_name']}.png")
    fig.savefig(f"benches/output/pdf/{result['param_name']}.pdf")
    fig.savefig(f"benches/output/svg/{result['param_name']}.svg")
