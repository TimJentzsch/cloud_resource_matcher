from __future__ import annotations
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from pulp import LpStatus, LpProblem

from optimizer.extensions.extension import ExtensionId
from optimizer.mixed_integer_program.solving import (
    SolveErrorReason,
    SolveError,
)
from optimizer.optimizer_toolbox_model.data import Cost
from optimizer.solver import Solver, get_pulp_solver
from ..extensions.decorators import DependencyInfo

if TYPE_CHECKING:
    # Avoid circular imports
    from .validated_optimizer import ValidatedOptimizer
    from .optimizer import Optimizer


class BuiltOptimizer:
    validated_optimizer: ValidatedOptimizer
    problem: LpProblem
    mip_data: dict[ExtensionId, Any]

    def __init__(
        self,
        validated_optimizer: ValidatedOptimizer,
        problem: LpProblem,
        mip_data: dict[ExtensionId, Any],
    ):
        self.validated_optimizer = validated_optimizer
        self.problem = problem
        self.mip_data = mip_data

    def optimizer(self) -> Optimizer:
        return self.validated_optimizer.optimizer

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> dict[ExtensionId, Any]:
        """Solve the optimization problem.

        :param solver: The solver to use to solve the mixed-integer program.
        :param time_limit: The maximum amount of time after which to
        stop the optimization.
        :param cost_gap_abs: The absolute cost tolerance for the solver to stop.
        :param cost_gap_rel: The relative cost tolerance for the solver to stop
        as a fraction. Must be a value between 0.0 and 1.0.
        """
        pulp_solver = get_pulp_solver(
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=cost_gap_abs,
            cost_gap_rel=cost_gap_rel,
        )

        # Solve the problem
        status_code = self.problem.solve(solver=pulp_solver)
        status = LpStatus[status_code]

        if status != "Optimal":
            raise SolveError(SolveErrorReason.INFEASIBLE)

        # Extract the solutions
        solution_info: dict[ExtensionId, DependencyInfo] = {
            e_id: extension.extract_solution()
            for e_id, extension in self.optimizer().extensions.items()
        }

        dependencies: dict[ExtensionId, set[ExtensionId]] = {
            e_id: info.dependencies for e_id, info in solution_info.items()
        }

        to_extract: dict[ExtensionId, set[ExtensionId]] = {**dependencies}

        solution_data: dict[ExtensionId, Any] = dict()

        while len(to_extract.keys()) > 0:
            # If an extension has no outstanding dependencies,
            # its solution can be extracted
            can_be_extracted = [
                e_id for e_id, deps in to_extract.items() if len(deps) == 0
            ]

            assert (
                len(can_be_extracted) > 0
            ), "Extensions can't be scheduled, dependency cycle detected"

            # Extract the solutions of each extension
            for e_id in can_be_extracted:
                info = solution_info[e_id]
                dependency_data = {
                    dep: self.optimizer().data[dep] for dep in info.dependencies
                }

                solution_data[e_id] = solution_info[e_id].action_fn(
                    mip_data=self.mip_data[e_id],
                    **dependency_data,
                )

            # Update the extensions that need to extract their solutions
            to_extract = {
                e_id: set(dep for dep in deps if dep not in can_be_extracted)
                for e_id, deps in to_extract.items()
                if e_id not in can_be_extracted
            }

        return solution_data
