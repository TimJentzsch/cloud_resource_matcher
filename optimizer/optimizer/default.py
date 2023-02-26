from __future__ import annotations

from datetime import timedelta
from typing import Self

from pulp import LpProblem

from optimizer.extensions import (
    BaseExtension,
    PerformanceExtension,
    NetworkExtension,
    MultiCloudExtension,
)
from optimizer.extensions.base import BaseSolution
from optimizer.optimizer.built_optimizer import BuiltOptimizer
from optimizer.optimizer.optimizer import Optimizer
from optimizer.optimizer.validated_optimizer import ValidatedOptimizer
from optimizer.extensions.data import (
    BaseData,
    PerformanceData,
    NetworkData,
    MultiCloudData,
)
from optimizer.extensions.data.types import Cost
from optimizer.solver import Solver


class DefaultOptimizer:
    """
    The default optimizer which includes all built-in extensions:

    - BaseExtension (virtual machines, services, time, etc.)
    - PerformanceExtension (vCPU and RAM requirements)
    - NetworkExtension (location assignment, max latency requirements, network costs)
    - MultiCloudExtension (multi cloud scenario)
    """

    optimizer: Optimizer

    def __init__(self, base_data: BaseData):
        self.optimizer = Optimizer().register_extension(BaseExtension()).add_data("base", base_data)

    def with_performance_data(self, performance_data: PerformanceData) -> Self:
        self.optimizer.register_extension(PerformanceExtension()).add_data(
            "performance", performance_data
        )
        return self

    def with_network_data(self, network_data: NetworkData) -> Self:
        self.optimizer.register_extension(NetworkExtension()).add_data("network", network_data)
        return self

    def with_multi_cloud_data(self, multi_cloud_data: MultiCloudData) -> Self:
        self.optimizer.register_extension(MultiCloudExtension()).add_data(
            "multi_cloud", multi_cloud_data
        )
        return self

    def validate(self) -> _ValidatedDefaultOptimizer:
        return _ValidatedDefaultOptimizer(self.optimizer.validate())


class _ValidatedDefaultOptimizer:
    validated_optimizer: ValidatedOptimizer

    def __init__(self, validated_optimizer: ValidatedOptimizer):
        self.validated_optimizer = validated_optimizer

    def build_mip(self) -> _BuiltDefaultOptimizer:
        return _BuiltDefaultOptimizer(self.validated_optimizer.build_mip())


class _BuiltDefaultOptimizer:
    built_optimizer: BuiltOptimizer

    def __init__(self, built_optimizer: BuiltOptimizer):
        self.built_optimizer = built_optimizer

    def problem(self) -> LpProblem:
        return self.built_optimizer.problem

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> BaseSolution:
        solution_data = self.built_optimizer.solve(solver, time_limit, cost_gap_abs, cost_gap_rel)

        # TODO: Return the other solution data as well
        return solution_data["base"]
