from dataclasses import dataclass
from datetime import timedelta

from pulp import LpProblem, LpStatus

from optimizer.data.types import Cost
from optimizer.optimizer_v2.extension import Extension
from optimizer.solver import Solver, get_pulp_solver
from optimizer.solving import SolveError, SolveErrorReason


@dataclass
class SolveSettings:
    solver: Solver = Solver.CBC
    time_limit: timedelta | None = None
    cost_gap_abs: Cost | None = None
    cost_gap_rel: float | None = None


class SolveExt(Extension[None]):
    problem: LpProblem
    solve_settings: SolveSettings

    def __init__(self, problem: LpProblem, solve_settings: SolveSettings):
        self.problem = problem
        self.solve_settings = solve_settings

    def action(self) -> None:
        pulp_solver = get_pulp_solver(
            solver=self.solve_settings.solver,
            time_limit=self.solve_settings.time_limit,
            cost_gap_abs=self.solve_settings.cost_gap_abs,
            cost_gap_rel=self.solve_settings.cost_gap_rel,
        )

        # Solve the problem
        status_code = self.problem.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)
