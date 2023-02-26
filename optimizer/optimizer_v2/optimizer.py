from __future__ import annotations

from typing import Self, Optional

from .step import Step, StepData


class Optimizer:
    steps: list[Step]

    def add_step(self, step: Step) -> Self:
        self.steps.append(step)
        return self

    def initialize(self, step_data: Optional[StepData] = None) -> InitializedOptimizer:
        return InitializedOptimizer(self, step_data or dict())


class InitializedOptimizer:
    optimizer: Optimizer
    step_data: StepData

    def __init__(self, optimizer: Optimizer, step_data: StepData):
        self.optimizer = optimizer
        self.step_data = step_data

    def execute(self) -> StepData:
        for step in self.optimizer.steps:
            # Execute each step sequentially and update the step data
            self.step_data = step.initialize(self.step_data).execute()

        return self.step_data
