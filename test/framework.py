import math
from typing import Self, Optional, Dict, Set

import pulp
import pytest

from optimizer.model import (
    Model,
    SolveError,
    SolveErrorReason,
    SolveSolution,
    VmServiceMatching,
)


class Expect:
    _model: Model

    def __init__(self, model: Model):
        self._model = model

    def to_be_infeasible(self) -> "_ExpectInfeasible":
        """The given problem is unsolvable."""
        return _ExpectInfeasible(self._model)

    def to_be_feasible(self) -> "_ExpectFeasible":
        """The given problem has a solution."""
        return _ExpectFeasible(self._model)


class _ExpectResult(Expect):
    _variables: Optional[Set[str]] = None
    _variables_exclusive: bool = False

    def with_variables(self, variables: Set[str], *, exclusive: bool = False) -> Self:
        """Enforce that the model contains the given variables.

        :param variables: The variables that must be in the model.
        :param exclusive: If set to true, the model must not contain any other variables.
        """
        self._variables = variables
        self._variables_exclusive = self._variables_exclusive or exclusive
        return self

    def test(self):
        """Test all conditions."""
        if self._variables is not None:
            self._test_variables(self._variables, self._variables_exclusive)

    def _test_variables(self, expected_variables: Set[str], exclusive: bool):
        variables = [var.name for var in self._model.prob.variables()]
        missing_variables = [var for var in expected_variables if var not in variables]

        if len(missing_variables) > 0:
            pytest.fail(f"Missing variables: {missing_variables}")

        if exclusive:
            extra_variables = [
                var for var in variables if var not in expected_variables
            ]

            if len(extra_variables) > 0:
                pytest.fail(f"Extra (too many) variables: {extra_variables}")


class _ExpectInfeasible(_ExpectResult):
    def test(self):
        super().test()

        try:
            solution = self._model.solve()
            pytest.fail(f"Expected problem to be infeasible, got {solution}")
        except SolveError as err:
            assert err.reason == SolveErrorReason.INFEASIBLE


class _ExpectFeasible(_ExpectResult):
    _cost: Optional[float] = None
    _epsilon: Optional[float] = None

    _vm_service_matching: Optional[VmServiceMatching] = None

    _variable_values: Optional[Dict[str, float]] = None

    def with_cost(self, cost: float, *, epsilon: float = 0.01) -> Self:
        """Enforce that the solution has the given objective value (i.e. cost).

        :param cost: The cost that the solution has to have.
        :param epsilon: The margin of error for the cost (e.g. due to numerical errors).
        """
        self._cost = cost
        self._epsilon = epsilon
        return self

    def with_vm_service_matching(self, vm_service_matching: VmServiceMatching) -> Self:
        """Enforce that the virtual machines are matched to the given services."""
        self._vm_service_matching = vm_service_matching
        return self

    def with_variable_values(
        self, variable_values: Dict[str, float], *, exclusive: bool = False
    ) -> Self:
        """Enforce that the given variables exist and have the given values.

        :param variable_values: The variables that must be in the model and their values.
        :param exclusive: If set to true, the model must not contain any other variables.
        """
        # The variables must be in the model
        if not self._variables:
            self._variables = set(variable_values.keys())
        else:
            self._variables = self._variables.union(variable_values.keys())

        self._variable_values = variable_values
        self._variables_exclusive = self._variables_exclusive or exclusive
        return self

    def test(self):
        super().test()

        try:
            solution = self._model.solve()

            if self._variable_values is not None:
                self._test_variable_values(self._variable_values)

            if self._vm_service_matching is not None:
                self._test_vm_service_matching(solution, self._vm_service_matching)

            if self._cost is not None:
                self._test_cost(solution, self._cost, self._epsilon)
        except SolveError as err:
            self._print_model()
            pytest.fail(f"Expected problem to be feasible, got {err}")

    @staticmethod
    def _test_cost(solution: SolveSolution, expected_cost: float, epsilon: float):
        if math.fabs(solution.cost - expected_cost) > epsilon:
            pytest.fail(f"Expected cost of {expected_cost}, got {solution.cost}")

    @staticmethod
    def _test_vm_service_matching(
        solution: SolveSolution, expected_matching: VmServiceMatching
    ):
        assert solution.vm_service_matching == expected_matching

    def _test_variable_values(self, expected_values: Dict[str, float]):
        actual_values = {
            var.name: pulp.value(var)
            for var in self._model.prob.variables()
            if var.name in expected_values.keys()
        }
        wrong_values = []

        for var, expected in expected_values.items():
            actual = actual_values[var]

            if actual != expected:
                wrong_values.append(
                    {"var": var, "expected": expected, "actual": actual}
                )

        if len(wrong_values) > 0:
            pytest.fail(f"Wrong variable values: {wrong_values}")

    def _print_model(self, line_limit: int = 100):
        """Print out the LP model to debug infeasible problems."""
        print(self._model.get_lp_string(line_limit=line_limit))
