from __future__ import annotations

from datetime import timedelta
from typing import Optional, Self

from optimizer.data import BaseData, PerformanceData, NetworkData, MultiCloudData
from optimizer.data.types import Cost
from optimizer.default.steps import step_validate, step_build_mip, step_solve, step_extract_solution
from optimizer.extensions_v2.solve.solve import SolveSettings
from optimizer.optimizer_v2.optimizer import Optimizer
from optimizer.solver import Solver


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
        return _InitializedDefaultOptimizer(
            base_data=self.base_data,
            performance_data=self.performance_data,
            network_data=self.network_data,
            multi_cloud_data=self.multi_cloud_data,
        )


class _InitializedDefaultOptimizer:
    optimizer: Optimizer

    base_data: BaseData
    performance_data: Optional[PerformanceData] = None
    network_data: Optional[NetworkData] = None
    multi_cloud_data: Optional[MultiCloudData] = None

    def __init__(
        self,
        base_data: BaseData,
        performance_data: Optional[PerformanceData],
        network_data: Optional[NetworkData],
        multi_cloud_data: Optional[MultiCloudData],
    ):
        self.base_data = base_data
        self.performance_data = performance_data
        self.network_data = network_data
        self.multi_cloud_data = multi_cloud_data

        performance = performance_data is not None
        network = network_data is not None
        multi_cloud = multi_cloud_data is not None

        self.optimizer = (
            Optimizer()
            .add_step(
                step_validate(performance=performance, network=network, multi_cloud=multi_cloud)
            )
            .add_step(
                step_build_mip(performance=performance, network=network, multi_cloud=multi_cloud)
            )
            .add_step(step_solve())
            .add_step(step_extract_solution())
        )

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> None:
        self.optimizer.initialize(
            {
                BaseData: self.base_data,
                PerformanceData: self.performance_data,
                NetworkData: self.network_data,
                MultiCloudData: self.multi_cloud_data,
                SolveSettings: SolveSettings(solver, time_limit, cost_gap_abs, cost_gap_rel),
            }
        ).execute()

        # FIXME: Return solution
