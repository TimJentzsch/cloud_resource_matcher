"""Utility functions to plot the benchmark results."""
import matplotlib.pyplot as plt

from benches.utils.run import BenchmarkResult

LINE_WIDTH = 3


def plot_results(result: BenchmarkResult) -> None:
    """Create a line graph for the benchmark results."""
    model_sizes: list[int] = [
        measure["variable_count"] * measure["constraint_count"] for measure in result["measures"]
    ]
    # Take the average of all measurements
    optimization_times: list[float] = [
        sum(time["total"] for time in measure["times"]) / len(measure["times"])
        for measure in result["measures"]
    ]

    col_model_size = "black"
    col_optimization_time = "gray"

    fig, ax = plt.subplots()
    ax.set_xlabel(result["variation_name"])

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
    ax.set_ylabel("model size")

    # Optimization time plot
    ax2 = ax.twinx()
    (time_plot,) = ax2.plot(
        result["param_values"],
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
    fig.savefig(f"benches/output/png/{result['param_name']}.png")
    fig.savefig(f"benches/output/pdf/{result['param_name']}.pdf")
