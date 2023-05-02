"""Utility functions for the CLI usage of the benchmark tool."""
from typing import Any

from cloud_resource_matcher.solver import Solver, get_pulp_solver


def get_solver_from_args() -> Any:
    """Obtain a solver object from the CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark the optimizer.")
    parser.add_argument(
        "--solver",
        choices=["cbc", "gurobi", "scip", "fscip"],
        default="cbc",
        help="The solver to use to solve the mixed-integer program.",
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

    return get_pulp_solver(solver=solver, msg=False)
