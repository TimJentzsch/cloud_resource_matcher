from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Self, Type, Any

from .extension import Extension


class InjectionError(RuntimeError):
    pass


class ScheduleError(RuntimeError):
    pass


@dataclass
class ExtDependency:
    param: str
    annotation: Any


# Data which can be injected into an extension.
# The keys should be class objects which define the type of the data.
StepData = dict[Any, Any]


class Step:
    extensions: list[Type[Extension]]

    def __init__(self):
        self.extensions = []

    def register_extension(self, extension: Type[Extension]) -> Self:
        """
        Register an extension to use in this step.

        :param extension: The extension to register.
        :return: The same step, to use for function chaining.
        """
        self.extensions.append(extension)
        return self

    def initialize(self, step_data: StepData) -> InitializedStep:
        return InitializedStep(self, step_data)


class InitializedStep:
    step: Step
    step_data: StepData

    def __init__(self, step: Step, step_data: StepData):
        self.step = step
        self.step_data = step_data

    def extensions(self) -> list[Type[Extension]]:
        return self.step.extensions

    def execute(self) -> StepData:
        """
        Execute the step by executing the action of all extensions within it.

        The dependencies of each extension are injected automatically.

        :raises InjectionError: If the `__init__` or `action` methods are missing type annotations.
        This is necessary to inject the dependencies automatically.
        :raises ScheduleError: If the extensions can't be scheduled,
        e.g. due to circular dependencies.
        :return: The step data, including the one generated during this step.
        """
        dependencies = self._extension_dependencies()

        ext_to_execute = [ext for ext in self.extensions()]

        while len(ext_to_execute) > 0:
            has_executed = False

            for ext in ext_to_execute:
                missing_dependencies = [
                    dep for dep in dependencies[ext] if dep.annotation not in self.step_data.keys()
                ]

                if len(missing_dependencies) == 0:
                    # Create the data parameters to instantiate the extension
                    dep_data = {
                        dep.param: self.step_data[dep.annotation] for dep in dependencies[ext]
                    }
                    # Determine what type of data is created by the extension
                    data_annotation = inspect.signature(ext.action).return_annotation

                    if data_annotation is None:
                        raise InjectionError(
                            f"Extension {ext} is missing the return type "
                            "annotation for the .action method"
                        )

                    # Instantiate the extension, using the data it requires
                    ext_obj = ext(**dep_data)
                    # Execute the action of the extension and save the returned data
                    self.step_data[data_annotation] = ext_obj.action()

                    has_executed = True
                    ext_to_execute = [ext2 for ext2 in ext_to_execute if ext != ext2]

            # Protection against infinite loops in case of circular dependencies
            if not has_executed:
                raise ScheduleError(
                    "The extensions could not be scheduled, "
                    f"{ext_to_execute} have unfulfilled dependencies"
                )

        return self.step_data

    def _extension_dependencies(self) -> dict[Type[Extension], list[ExtDependency]]:
        """
        Determine which extension depends on which type of data.

        :return: For each extension, a list of its dependencies.
        """
        dependencies: dict[Type[Extension], list[ExtDependency]] = dict()

        # Collect the dependencies for each extension
        for ext in self.extensions():
            init_params = inspect.signature(ext.__init__).parameters

            ext_dependencies: list[ExtDependency] = []

            for param, signature in init_params.items():
                # We don't need to inject the `self` parameter, skip it
                if param == "self":
                    continue

                annotation = signature.annotation

                if annotation is None:
                    raise InjectionError(
                        f"The __init__ method of extension {ext} "
                        "needs type annotation on its parameters. "
                        "This is needed to properly inject the dependencies."
                    )

                ext_dependencies.append(ExtDependency(param=param, annotation=annotation))

            dependencies[ext] = ext_dependencies

        return dependencies
