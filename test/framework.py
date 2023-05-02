"""A testing framework for the cloud resource matcher."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Self

import pytest
from optiframe import InfeasibleError, SolutionObjValue
from optiframe.framework import BuiltOptimizer, InitializedOptimizer
from pulp import LpProblem, LpVariable

from cloud_resource_matcher.modules.base import BaseSolution
from cloud_resource_matcher.modules.base.data import CloudResource, CloudService, Cost
from cloud_resource_matcher.modules.base.extract_solution import (
    CrToCsMatching,
    ServiceInstanceCount,
)


@dataclass
class SolveSolution:
    """The solution obtained from solving the tested instance."""

    cost: Cost
    base: BaseSolution


class Expect:
    """Create a test for the given optimizer instance."""

    _optimizer: BuiltOptimizer

    _variables: set[str]
    _variables_exclusive: bool = False

    _fixed_variable_values: dict[str, float]

    def __init__(self, optimizer: InitializedOptimizer):
        self._optimizer = optimizer.validate().pre_processing().build_mip()
        self._variables = set()
        self._fixed_variable_values = dict()

    def _problem(self) -> LpProblem:
        return self._optimizer.problem()

    def _with_variables(self, variables: Iterable[str], *, exclusive: bool = False) -> Self:
        """Enforce that the model contains the given variables.

        :param variables: The variables that must be in the model.
        :param exclusive: If true, the model must not contain any other variables.
        """
        self._variables = self._variables.union(variables)
        self._variables_exclusive = self._variables_exclusive or exclusive
        return self

    def with_fixed_variable_values(self, fixed_values: Dict[str, float]) -> Self:
        """Fix the values of the given variables."""
        # The variables must be in the model
        self._with_variables(fixed_values.keys())

        for var_name, value in fixed_values.items():
            print(f"name {var_name} value {value}")
            self._fixed_variable_values[var_name] = value

        return self

    def with_fixed_cr_to_cs_matching(
        self, matching: dict[tuple[CloudResource, CloudService], int]
    ) -> Self:
        """Fix the values of the variables defined by the given CR-CS matching."""
        self.with_fixed_variable_values(
            {f"cr_to_cs_matching({cr},{cs})": val for (cr, cs), val in matching.items()}
        )
        return self

    def to_be_infeasible(self) -> _ExpectInfeasible:
        """Assert that the problem is unsolvable."""
        return _ExpectInfeasible(self)

    def to_be_feasible(self) -> _ExpectFeasible:
        """Assert that the problem has a valid solution."""
        return _ExpectFeasible(self)


class _ExpectResult:
    _expect: Expect

    def __init__(self, expect: Expect):
        self._expect = expect

    def test(self) -> None:
        """Test all conditions."""
        # First, fix the model's variables to the given values, if applicable
        self._fix_variable_values()

        # Then test stuff
        self._test_variables()

    def with_variables(self, variables: Iterable[str], *, exclusive: bool = False) -> Self:
        """Enforce that the model contains the given variables.

        :param variables: The variables that must be in the model.
        :param exclusive: If set to true, the model must not contain
        any other variables.
        """
        self._expect._with_variables(variables, exclusive=exclusive)
        return self

    def _problem(self) -> LpProblem:
        return self._expect._problem()

    def _solve(self) -> SolveSolution:
        data = self._expect._optimizer.print_mip_and_solve()
        return SolveSolution(cost=data[SolutionObjValue].objective_value, base=data[BaseSolution])

    def _fix_variable_values(self) -> None:
        # The warning here is invalid, the type is incorrectly specified in PuLP
        variables: List[LpVariable] = self._problem().variables()

        for var_name, value in self._expect._fixed_variable_values.items():
            for var in variables:
                if var.name == var_name:
                    var.setInitialValue(value)
                    var.fixValue()
                    break

    def _test_variables(self) -> None:
        variables = [var.name for var in self._problem().variables()]
        missing_variables = [var for var in self._expect._variables if var not in variables]
        for var in missing_variables:
            assert var not in variables

        if len(missing_variables) > 0:
            pytest.fail(f"Missing variables: {missing_variables}")

        if self._expect._variables_exclusive:
            extra_variables = [var for var in variables if var not in self._expect._variables]

            if len(extra_variables) > 0:
                pytest.fail(f"Extra (too many) variables: {extra_variables}")


class _ExpectInfeasible(_ExpectResult):
    def __init__(self, expect: Expect):
        super(_ExpectInfeasible, self).__init__(expect)

    def test(self) -> None:
        super(_ExpectInfeasible, self).test()

        try:
            solution = self._solve()
            pytest.fail(f"Expected problem to be infeasible, got {solution}")
        except InfeasibleError:
            pass


class _ExpectFeasible(_ExpectResult):
    _cost: Optional[float] = None
    _epsilon: Optional[float] = None

    _cr_to_cs_matching: Optional[CrToCsMatching] = None
    _cs_instance_count: Optional[ServiceInstanceCount] = None

    _variable_values: Dict[str, float]

    def __init__(self, expect: Expect):
        super(_ExpectFeasible, self).__init__(expect)
        self._variable_values = dict()

    def with_cost(self, cost: float, *, epsilon: float = 0.01) -> Self:
        """Enforce that the solution has the given objective value (i.e. cost).

        :param cost: The cost that the solution has to have.
        :param epsilon: The margin of error for the cost (e.g. due to numerical errors).
        """
        self._cost = cost
        self._epsilon = epsilon
        return self

    def with_cr_to_cs_matching(self, cr_to_cs_matching: CrToCsMatching) -> Self:
        """Enforce that the cloud resources are matched to the given cloud services."""
        self._cr_to_cs_matching = cr_to_cs_matching

        return self

    def with_cs_instance_count(self, cs_instance_count: ServiceInstanceCount) -> Self:
        """Enforce that the right amount of instances are bought for each cloud service."""
        self._cs_instance_count = cs_instance_count

        return self

    def with_variable_values(
        self, variable_values: Dict[str, float], *, exclusive: bool = False
    ) -> Self:
        """Enforce that the given variables exist and have the given values.

        :param variable_values: The variables and their values that
        must be in the model.
        :param exclusive: If true, the model must not contain any other variables.
        """
        print("Variable values", variable_values)
        # The variables must be in the model
        self._expect._with_variables(variable_values.keys(), exclusive=exclusive)

        for var_name, value in variable_values.items():
            self._variable_values[var_name] = value

        return self

    def test(self) -> None:
        super(_ExpectFeasible, self).test()

        try:
            solution = self._solve()

            self._test_variable_values()
            self._test_cr_to_cs_matching(solution)
            self._test_cs_instance_count(solution)
            self._test_cost(solution)
        except InfeasibleError:
            self._print_model()
            pytest.fail("Expected problem to be feasible, but it was infeasible")

    def _test_cost(self, solution: SolveSolution) -> None:
        if self._cost is None or self._epsilon is None:
            return

        if math.fabs(solution.cost - self._cost) > self._epsilon:
            pytest.fail(f"Expected cost of {self._cost}, got {solution.cost}")

    def _test_cr_to_cs_matching(self, solution: SolveSolution) -> None:
        if self._cr_to_cs_matching is None:
            return

        actual = solution.base.cr_to_cs_matching
        expected = self._cr_to_cs_matching

        assert (
            actual == expected
        ), f"Different CR to CS matching than expected\n{actual}\n!= {expected}"

    def _test_cs_instance_count(self, solution: SolveSolution) -> None:
        if self._cs_instance_count is None:
            return

        actual = solution.base.cs_instance_count
        expected = self._cs_instance_count

        assert (
            actual == expected
        ), "Different CS instance counts than expected\n{actual}\n!= {expected}"

    def _test_variable_values(self) -> None:
        actual_values = {
            var.name: var.value()
            for var in self._problem().variables()
            if var.name in self._variable_values.keys()
        }
        wrong_values = []

        for var, expected in self._variable_values.items():
            actual = actual_values[var]

            if actual != expected:
                wrong_values.append({"var": var, "expected": expected, "actual": actual})

        if len(wrong_values) > 0:
            pytest.fail(f"Wrong variable values: {wrong_values}")

    def _print_model(self, line_limit: int = 100) -> None:
        """Print out the LP model to debug infeasible problems."""
        print(self._expect._optimizer.get_lp_string(line_limit=line_limit))
