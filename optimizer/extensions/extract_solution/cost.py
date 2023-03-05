from dataclasses import dataclass

from pulp import LpProblem

from optimizer.data.types import Cost
from optimizer.optimizer.extension import Extension


@dataclass
class SolutionCost:
    """The total cost of the solution."""

    cost: Cost


class ExtractSolutionCostExt(Extension[SolutionCost]):
    problem: LpProblem

    def __init__(self, problem: LpProblem):
        self.problem = problem

    def action(self) -> SolutionCost:
        cost = self.problem.objective.value()

        return SolutionCost(cost)
