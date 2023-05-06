"""Utility functions for the CLI usage of the benchmark tool."""
from dataclasses import dataclass
from typing import Any

from cloud_resource_matcher.solver import Solver, get_pulp_solver


@dataclass
class CliArgs:
    """The CLI arguments for the benchmark tools."""

    solver: Any
    measures: int
    use_cache: bool


def get_cli_args() -> CliArgs:
    """Obtain a solver object from the CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark the optimizer.")
    parser.add_argument(
        "--solver",
        choices=["cbc", "gurobi", "scip", "fscip"],
        default="cbc",
        help="The solver to use to solve the mixed-integer program.",
    )
    parser.add_argument(
        "--measures",
        type=int,
        default=0,
        help="The number of measures to take for each benchmark.",
    )
    parser.add_argument(
        "--use-cache",
        type=bool,
        action="store_true",
        default=False,
        help="Use the cached JSON measurements, only regenerate the plots.",
    )

    args = parser.parse_args()

    if args.solver == "cbc":
        solver = Solver.CBC
    elif args.solver == "gurobi":
        solver = Solver.GUROBI
    elif args.solver == "scip":
        solver = Solver.SCIP
    elif args.solver == "fscip":
        solver = Solver.FSCIP
    else:
        raise RuntimeError(f"Unsupported solver {args.solver}")

    return CliArgs(
        solver=get_pulp_solver(solver=solver, msg=False),
        measures=args.measures,
        use_cache=args.use_cache,
    )
