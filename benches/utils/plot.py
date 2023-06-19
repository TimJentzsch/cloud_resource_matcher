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
    col_foreground = "white" if dark_theme else "black"
    col_model_size = "#93bce1" if dark_theme else "black"
    col_optimization_time = "#b993e1" if dark_theme else "gray"

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()
    ax.set_xlabel(result["variation_name"], color=col_foreground)

    # Model size plot
    (size_plot,) = ax.plot(
        result["param_values"],
        model_sizes,
        label="model size",
        color=col_model_size,
        marker="o",
        linewidth=LINE_WIDTH,
    )

    configure_axes(ax, "model size", col_background, col_foreground)

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

    configure_axes(ax2, "total optimization time (s)", col_background, col_foreground)

    # Legend
    ax.legend(
        handles=[size_plot, time_plot],
        labelcolor=col_foreground,
        edgecolor=col_foreground,
        facecolor=col_background,
    )

    fig.patch.set_facecolor(col_background)

    # Save the plot
    fig.savefig(f"benches/output/png/{result['param_name']}.png")
    fig.savefig(f"benches/output/pdf/{result['param_name']}.pdf")
    fig.savefig(f"benches/output/svg/{result['param_name']}.svg")


def configure_axes(axes: Axes, label: str, col_background: str, col_foreground: str) -> None:
    """Configure common properties of an axes."""
    axes.set_ylim(bottom=0)
    axes.set_ylabel(label, color=col_foreground)

    axes.patch.set_facecolor(col_background)
    axes.xaxis.set_tick_params(color=col_foreground, labelcolor=col_foreground)
    axes.yaxis.set_tick_params(color=col_foreground, labelcolor=col_foreground)

    for spine in axes.spines.values():
        spine.set_edgecolor(col_foreground)
