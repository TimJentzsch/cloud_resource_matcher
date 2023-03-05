from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Self, Type, Any

from .extension import Extension


logger = logging.getLogger(__name__)


class InjectionError(RuntimeError):
    pass


class ScheduleError(RuntimeError):
    pass


@dataclass
class ExtDependency:
    param: str
    annotation: Any

    def __repr__(self):
        return f"{self.param}: {self.annotation.__name__}"

    def __str__(self):
        return f"{self.param}: {self.annotation.__name__}"


# Data which can be injected into an extension.
# The keys should be class objects which define the type of the data.
StepData = dict[Any, Any]


class Step:
    name: str
    extensions: list[Type[Extension]]

    def __init__(self, name: str):
        self.name = name
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

    def name(self) -> str:
        return self.step.name

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
        start_time = datetime.now()
        logger.info(f"Executing step {self.name()}...")

        dependencies = self._extension_dependencies()

        ext_to_execute = [ext for ext in self.extensions()]

        while len(ext_to_execute) > 0:
            has_executed = False

            missing_dependencies = {
                ext: [
                    dep for dep in dependencies[ext] if dep.annotation not in self.step_data.keys()
                ]
                for ext in ext_to_execute
            }

            for ext in ext_to_execute:
                if len(missing_dependencies[ext]) == 0:
                    # Create the data parameters to instantiate the extension
                    dep_data = {
                        dep.param: self.step_data[dep.annotation] for dep in dependencies[ext]
                    }
                    # Determine what type of data is created by the extension
                    data_annotation = inspect.signature(ext.action).return_annotation

                    # Instantiate the extension, using the data it requires
                    ext_obj = ext(**dep_data)

                    # Execute the action of the extension and save the returned data
                    data = ext_obj.action()

                    if data is None and data_annotation is not None:
                        raise InjectionError(
                            f"Extension {ext} returned data, but has not type annotation for it. "
                            "This prevents the data from being accessible to other extensions."
                        )
                    elif data is not None:
                        # Make the data available to other extensions
                        self.step_data[data_annotation] = data

                    has_executed = True
                    ext_to_execute = [ext2 for ext2 in ext_to_execute if ext != ext2]

            # Protection against infinite loops in case of circular or missing dependencies
            if not has_executed:
                ext_strs = [ext.__name__ for ext in ext_to_execute]
                missing_deps_strs = "\n".join(
                    f"- {ext.__name__}: {missing_deps}"
                    for ext, missing_deps in missing_dependencies.items()
                )
                raise ScheduleError(
                    "The extensions could not be scheduled, "
                    f"{ext_strs} have unfulfilled dependencies:\n"
                    f"{missing_deps_strs}"
                )

        duration = datetime.now() - start_time

        logger.info(f"Finished step {self.name()} in {duration.total_seconds():.2f}s.")

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
