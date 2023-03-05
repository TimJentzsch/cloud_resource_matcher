from __future__ import annotations

import tempfile
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Self

from pulp import LpProblem

from optimizer.data import BaseData, PerformanceData, NetworkData, MultiCloudData
from optimizer.data.types import Cost
from optimizer.default.steps import step_validate, step_build_mip, step_solve, step_extract_solution
from optimizer.extensions_v2.extract_solution.base import BaseSolution
from optimizer.extensions_v2.extract_solution.cost import SolutionCost
from optimizer.extensions_v2.solve.solve import SolveSettings
from optimizer.optimizer_v2.optimizer import Optimizer, InitializedOptimizer
from optimizer.solver import Solver


@dataclass
class SolveSolution:
    cost: Cost
    base: BaseSolution


class DefaultOptimizer:
    """
    The default optimizer which includes all built-in extensions:

    - BaseExtension (virtual machines, services, time, etc.)
    - PerformanceExtension (vCPU and RAM requirements)
    - NetworkExtension (location assignment, max latency requirements, network costs)
    - MultiCloudExtension (multi cloud scenario)
    """

    base_data: BaseData
    performance_data: Optional[PerformanceData] = None
    network_data: Optional[NetworkData] = None
    multi_cloud_data: Optional[MultiCloudData] = None

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def with_performance_data(self, performance_data: PerformanceData) -> Self:
        self.performance_data = performance_data
        return self

    def with_network_data(self, network_data: NetworkData) -> Self:
        self.network_data = network_data
        return self

    def with_multi_cloud_data(self, multi_cloud_data: MultiCloudData) -> Self:
        self.multi_cloud_data = multi_cloud_data
        return self

    def initialize(self) -> _InitializedDefaultOptimizer:
        performance = self.performance_data is not None
        network = self.network_data is not None
        multi_cloud = self.multi_cloud_data is not None

        initialized_optimizer = (
            Optimizer()
            .add_step(
                step_validate(performance=performance, network=network, multi_cloud=multi_cloud)
            )
            .add_step(
                step_build_mip(performance=performance, network=network, multi_cloud=multi_cloud)
            )
            .add_step(step_solve())
            .add_step(step_extract_solution())
            .initialize(
                self.base_data, self.performance_data, self.network_data, self.multi_cloud_data
            )
        )
        return _InitializedDefaultOptimizer(initialized_optimizer)


class _InitializedDefaultOptimizer:
    optimizer: InitializedOptimizer

    def __init__(self, optimizer: InitializedOptimizer):
        self.optimizer = optimizer

    def validate(self) -> _ValidatedDefaultOptimizer:
        self.optimizer.execute_step(0)
        return _ValidatedDefaultOptimizer(self.optimizer)

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> SolveSolution:
        return self.validate().build_mip().solve(solver, time_limit, cost_gap_abs, cost_gap_rel)


class _ValidatedDefaultOptimizer:
    optimizer: InitializedOptimizer

    def __init__(self, optimizer: InitializedOptimizer):
        self.optimizer = optimizer

    def build_mip(self) -> _BuiltDefaultOptimizer:
        self.optimizer.execute_step(1)
        return _BuiltDefaultOptimizer(self.optimizer)


class _BuiltDefaultOptimizer:
    optimizer: InitializedOptimizer

    def __init__(self, optimizer: InitializedOptimizer):
        self.optimizer = optimizer

    def problem(self) -> LpProblem:
        return self.optimizer.step_data[LpProblem]

    def get_lp_string(self, line_limit: int = 100) -> str:
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".lp") as file:
            self.problem().writeLP(filename=file.name)
            return "".join(file.readlines()[:line_limit])

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> SolveSolution:
        self.optimizer.add_data(SolveSettings(solver, time_limit, cost_gap_abs, cost_gap_rel))

        # Solve the MIP
        self.optimizer.execute_step(2)
        # Extract the solution
        step_data = self.optimizer.execute_step(3)

        return SolveSolution(
            cost=step_data[SolutionCost].cost,
            base=step_data[BaseSolution],
        )
