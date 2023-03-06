from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Self, Type, Any

from optimizer.workflow_engine import Step
from optimizer.workflow_engine.task import Task
from optimizer.workflow_engine.workflow import Workflow, InitializedWorkflow

from .tasks import CreateProblemTask, CreateObjectiveTask, SolveTask, SolveSettings, ExtractSolutionCostTask
from ..data.types import Cost
from ..solver import Solver
from ..workflow_engine.step import StepData


@dataclass
class OptimizationPackage:
    build_mip: Type[Task]
    validate: Optional[Type[Task[None]]] = None
    extract_solution: Optional[Type[Task]] = None


class Optimizer:
    packages: list[OptimizationPackage]

    def __init__(self):
        self.packages = []

    def add_package(self, package: OptimizationPackage) -> Self:
        self.packages.append(package)
        return self

    def initialize(self, *data: Any) -> InitializedOptimizer:
        validate_step = Step("validate")
        build_mip_step = Step("build_mip").add_task(CreateProblemTask).add_task(CreateObjectiveTask)
        solve_step = Step("solve").add_task(SolveTask)
        extract_solution_step = Step("extract_solution").add_task(ExtractSolutionCostTask)

        for package in self.packages:
            if package.validate is not None:
                validate_step.add_task(package.validate)

            build_mip_step.add_task(package.build_mip)

            if package.extract_solution is not None:
                extract_solution_step.add_task(package.extract_solution)

        workflow = (
            Workflow()
            .add_step(validate_step)
            .add_step(build_mip_step)
            .add_step(solve_step)
            .add_step(extract_solution_step)
            .initialize(*data)
        )
        return InitializedOptimizer(workflow)


class InitializedOptimizer:
    workflow: InitializedWorkflow

    def __init__(self, workflow: InitializedWorkflow):
        self.workflow = workflow

    def validate(self) -> ValidatedOptimizer:
        self.workflow.execute_step(0)
        return ValidatedOptimizer(self.workflow)


class ValidatedOptimizer:
    workflow: InitializedWorkflow

    def __init__(self, workflow: InitializedWorkflow):
        self.workflow = workflow

    def build_mip(self) -> BuiltOptimizer:
        self.workflow.execute_step(1)
        return BuiltOptimizer(self.workflow)


class BuiltOptimizer:
    workflow: InitializedWorkflow

    def __init__(self, workflow: InitializedWorkflow):
        self.workflow = workflow

    def solve(
        self,
        solver: Solver = Solver.CBC,
        time_limit: timedelta | None = None,
        cost_gap_abs: Cost | None = None,
        cost_gap_rel: float | None = None,
    ) -> StepData:
        self.workflow.add_data(SolveSettings(solver, time_limit, cost_gap_abs, cost_gap_rel))
        self.workflow.execute_step(2)
        return self.workflow.execute_step(3)
