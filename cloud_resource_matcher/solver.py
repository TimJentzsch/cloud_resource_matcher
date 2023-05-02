"""Utilities to easily create a solver object."""

from datetime import timedelta
from enum import Enum
from typing import Any, Optional

import pulp

from cloud_resource_matcher.modules.base.data import Cost


class Solver(Enum):
    """Popular solvers for mixed integer programs."""

    # COIN Branch and Cut solver (CBC), an open source solver.
    # Comes pre-bundled with Pulp.
    # <https://coin-or.github.io/Cbc/intro.html>
    CBC = 0

    # Gurobi, a fast commercial solver.
    # <https://www.gurobi.com/>
    GUROBI = 1

    # Solving Constraint Integer Programs (SCIP), a modular open source solver.
    # <https://scipopt.org/>
    SCIP = 2

    # A parallelized version of SCIP.
    # <https://ug.zib.de>
    FSCIP = 3


def get_pulp_solver(
    solver: Solver = Solver.CBC,
    time_limit: Optional[timedelta] = None,
    cost_gap_abs: Optional[Cost] = None,
    cost_gap_rel: Optional[float] = None,
    msg: bool = True,
) -> Any:
    """Get the corresponding pulp solver for the solver type."""
    time_limit_sec = None if time_limit is None else time_limit.total_seconds()

    base_params = dict(timeLimit=time_limit_sec, gapAbs=cost_gap_abs, gapRel=cost_gap_rel, msg=msg)

    if solver == Solver.CBC:
        return pulp.PULP_CBC_CMD(**base_params)
    elif solver == Solver.GUROBI:
        return pulp.GUROBI_CMD(**base_params)
    elif solver == Solver.SCIP:
        scip_options = [
            "set presolving emphasis aggressive",
            "set heuristics emphasis aggressive",
        ]
        return pulp.SCIP_CMD(**base_params, options=scip_options)
    elif solver == Solver.FSCIP:
        return pulp.FSCIP_CMD(**base_params)
    else:
        raise RuntimeError(f"Unsupported solver '{solver}'")
