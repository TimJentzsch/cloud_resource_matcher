from __future__ import annotations

from typing import Self, Any

from .step import Step, StepData


class Optimizer:
    steps: list[Step]

    def __init__(self):
        self.steps = list()

    def add_step(self, step: Step) -> Self:
        self.steps.append(step)
        return self

    def initialize(self, *args: Any) -> InitializedOptimizer:
        step_data = {type(data): data for data in args if data is not None}

        return InitializedOptimizer(self, step_data)


class InitializedOptimizer:
    optimizer: Optimizer
    step_data: StepData

    def __init__(self, optimizer: Optimizer, step_data: StepData):
        self.optimizer = optimizer
        self.step_data = step_data

    def add_data(self, data: Any) -> Self:
        data_type = type(data)
        self.step_data[data_type] = data
        return self

    def execute_step(self, index: int) -> StepData:
        step = self.optimizer.steps[index]
        self.step_data = step.initialize(self.step_data).execute()
        return self.step_data

    def execute(self) -> StepData:
        for step in self.optimizer.steps:
            # Execute each step sequentially and update the step data
            self.step_data = step.initialize(self.step_data).execute()

        return self.step_data
