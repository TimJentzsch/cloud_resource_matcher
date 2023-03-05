from dataclasses import dataclass
from datetime import timedelta

from pulp import LpProblem, LpMinimize, LpAffineExpression, LpStatus

from optimizer.data.types import Cost
from optimizer.solver import Solver, get_pulp_solver
from optimizer.solving import SolveError, SolveErrorReason
from optimizer.workflow_engine import Task


class CreateProblemTask(Task[LpProblem]):
    def __init__(self):
        pass

    def execute(self) -> LpProblem:
        # TODO: Add way to change name and min/max target
        return LpProblem("optimization_problem", LpMinimize)


class CreateObjectiveTask(Task[LpAffineExpression]):
    def __init__(self):
        pass

    def execute(self) -> LpAffineExpression:
        return LpAffineExpression()


@dataclass
class SolveSettings:
    solver: Solver = Solver.CBC
    time_limit: timedelta | None = None
    cost_gap_abs: Cost | None = None
    cost_gap_rel: float | None = None


class SolveTask(Task[None]):
    problem: LpProblem
    objective: LpAffineExpression
    solve_settings: SolveSettings

    def __init__(
        self, problem: LpProblem, objective: LpAffineExpression, solve_settings: SolveSettings
    ):
        self.problem = problem
        self.objective = objective
        self.solve_settings = solve_settings

    def execute(self) -> None:
        # Add objective to MIP
        self.problem.setObjective(self.objective)

        # Assemble the solver
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
