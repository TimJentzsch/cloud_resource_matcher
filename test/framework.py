import math
from typing import List, Self, Optional, Dict

import pulp
import pytest

from optimizer.model import Model, SolveError, SolveErrorReason, SolveSolution


class Expect:
    model: Model

    def __init__(self, model: Model):
        self.model = model

    def to_be_infeasible(self) -> "_ExpectInfeasible":
        """The given problem is unsolvable."""
        return _ExpectInfeasible(self.model)

    def to_be_feasible(self) -> "_ExpectFeasible":
        """The given problem has a solution."""
        return _ExpectFeasible(self.model)


class _ExpectResult(Expect):
    variables: Optional[List[str]] = None
    variables_exclusive: bool = False
    variable_values: Optional[Dict[str, float]] = None

    def with_variables(self, variables: List[str], exclusive: bool = False) -> Self:
        """Enforce that the model contains the given variables.

        :param variables: The variables that must be in the model.
        :param exclusive: If set to true, the model must not contain any other variables.
        """
        self.variables = variables
        self.variables_exclusive = self.variables_exclusive or exclusive
        return self

    def with_variable_values(
        self, variable_values: Dict[str, float], exclusive: bool = False
    ) -> Self:
        """Enforce that the given variables have the given values.

        :param variable_values: The variables that must be in the model and their values.
        :param exclusive: If set to true, the model must not contain any other variables.
        """
        self.variable_values = variable_values
        self.variables_exclusive = self.variables_exclusive or exclusive
        return self

    def _test_variables(self, expected_variables: List[str], exclusive: bool):
        variables = self.model.prob.variables()
        missing_variables = [var for var in expected_variables if var not in variables]

        if len(missing_variables) > 0:
            pytest.fail(f"Missing variables: {missing_variables}")

        if exclusive:
            extra_variables = [
                var for var in variables if var not in expected_variables
            ]

            if len(extra_variables) > 0:
                pytest.fail(f"Extra (too many) variables: {extra_variables}")

    @staticmethod
    def _test_variable_values(expected_values: Dict[str, float]):
        wrong_values = []

        for var, expected in expected_values.items():
            actual = pulp.value(var)

            if actual != expected:
                wrong_values.append({"expected": expected, "actual": actual})

        if len(wrong_values) > 0:
            pytest.fail(f"Wrong variable values: {wrong_values}")

    def test(self):
        """Test all conditions."""
        if self.variables is not None or self.variable_values is not None:
            expected_variables = self.variables + [
                var for var in self.variable_values.keys() if var not in self.variables
            ]
            self._test_variables(expected_variables, self.variables_exclusive)

            if self.variable_values is not None:
                self._test_variable_values(self.variable_values)


class _ExpectInfeasible(_ExpectResult):
    def test(self):
        super().test()

        try:
            solution = self.model.solve()
            pytest.fail(f"Expected problem to be infeasible, got {solution}")
        except SolveError as err:
            assert err.reason == SolveErrorReason.INFEASIBLE


class _ExpectFeasible(_ExpectResult):
    objective_value: Optional[float] = None
    epsilon: Optional[float] = None

    def with_objective_value(self, objective_value: float, epsilon: float = 0.01) -> Self:
        """Enforce that the solution has the given objective value (i.e. cost).

        :param objective_value: The cost that the solution has to have.
        :param epsilon: The margin of error for the cost (e.g. due to numerical errors).
        """
        self.objective_value = objective_value
        self.epsilon = epsilon

    @staticmethod
    def _test_cost(solution: SolveSolution, expected_obj_value: float, epsilon: float):
        if math.fabs(solution.cost - expected_obj_value) > epsilon:
            pytest.fail(f"Expected objective value of {expected_obj_value}, got {solution.cost}")

    def test(self):
        super().test()

        try:
            solution = self.model.solve()

            if self.objective_value is not None:
                self._test_cost(solution, self.objective_value, self.epsilon)
        except SolveError as err:
            pytest.fail(f"Expected problem to be feasible, got {err}")
