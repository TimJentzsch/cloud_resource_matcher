from __future__ import annotations

import math
from typing import Self, Optional, Dict, List, Iterable

import pytest
from pulp import LpVariable, LpProblem

from optimizer.default.optimizer import (
    DefaultOptimizer,
    _BuiltDefaultOptimizer,
    SolveSolution,
)
from optimizer.extensions_v2.extract_solution.base import VmServiceMatching, ServiceInstanceCount
from optimizer.solving import (
    SolveErrorReason,
    SolveError,
)
from optimizer.data.types import Service, VirtualMachine


class Expect:
    _optimizer: _BuiltDefaultOptimizer

    _variables: set[str]
    _variables_exclusive: bool = False

    _fixed_variable_values: dict[str, float]

    def __init__(self, optimizer: DefaultOptimizer):
        self._optimizer = optimizer.initialize().validate().build_mip()
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

    def with_fixed_vm_service_matching(
        self, matching: dict[tuple[VirtualMachine, Service], int]
    ) -> Self:
        """Fix the values of the variables defined by the given VM-service matching."""
        self.with_fixed_variable_values(
            {f"vm_matching({v},{s})": val for (v, s), val in matching.items()}
        )
        return self

    def to_be_infeasible(self) -> _ExpectInfeasible:
        """The given problem is unsolvable."""
        return _ExpectInfeasible(self)

    def to_be_feasible(self) -> _ExpectFeasible:
        """The given problem has a solution."""
        return _ExpectFeasible(self)


class _ExpectResult:
    _expect: Expect

    def __init__(self, expect: Expect):
        self._expect = expect

    def test(self):
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
        return self._expect._optimizer.solve()

    def _fix_variable_values(self):
        # The warning here is invalid, the type is incorrectly specified in PuLP
        variables: List[LpVariable] = self._problem().variables()

        for var_name, value in self._expect._fixed_variable_values.items():
            for var in variables:
                if var.name == var_name:
                    var.setInitialValue(value)
                    var.fixValue()
                    break

    def _test_variables(self):
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

    def test(self):
        super(_ExpectInfeasible, self).test()

        try:
            solution = self._solve()
            pytest.fail(f"Expected problem to be infeasible, got {solution}")
        except SolveError as err:
            assert err.reason == SolveErrorReason.INFEASIBLE


class _ExpectFeasible(_ExpectResult):
    _cost: Optional[float] = None
    _epsilon: Optional[float] = None

    _vm_service_matching: Optional[VmServiceMatching] = None
    _service_instance_count: Optional[ServiceInstanceCount] = None

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

    def with_vm_service_matching(self, vm_service_matching: VmServiceMatching) -> Self:
        """Enforce that the virtual machines are matched to the given services."""
        self._vm_service_matching = vm_service_matching

        return self

    def with_service_instance_count(self, service_instance_count: ServiceInstanceCount) -> Self:
        """Enforce that the right amount of instances are bought for each service."""
        self._service_instance_count = service_instance_count

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

    def test(self):
        super(_ExpectFeasible, self).test()

        try:
            solution = self._solve()

            self._test_variable_values()
            self._test_vm_service_matching(solution)
            self._test_service_instance_count(solution)
            self._test_cost(solution)
        except SolveError as err:
            self._print_model()
            pytest.fail(f"Expected problem to be feasible, got {err}")

    def _test_cost(self, solution: SolveSolution):
        if self._cost is None or self._epsilon is None:
            return

        if math.fabs(solution.cost - self._cost) > self._epsilon:
            pytest.fail(f"Expected cost of {self._cost}, got {solution.cost}")

    def _test_vm_service_matching(self, solution: SolveSolution):
        if self._vm_service_matching is None:
            return

        assert (
            solution.base.vm_service_matching == self._vm_service_matching
        ), "Different VM/Service matching than expected"

    def _test_service_instance_count(self, solution: SolveSolution):
        if self._service_instance_count is None:
            return

        assert (
            solution.base.service_instance_count == self._service_instance_count
        ), "Different service instance counts than expected"

    def _test_variable_values(self):
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

    def _print_model(self, line_limit: int = 100):
        """Print out the LP model to debug infeasible problems."""
        print(self._expect._optimizer.get_lp_string(line_limit=line_limit))
