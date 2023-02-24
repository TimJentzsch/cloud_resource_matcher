import inspect
from dataclasses import dataclass
from typing import Self, Type, Any

from .extension import Extension


@dataclass
class ExtDependency:
    param: str
    annotation: Any


class Step:
    extensions: list[Type[Extension]]

    def __init__(self):
        self.extensions = []

    def register_extension(self, extension: Type[Extension]) -> Self:
        self.extensions.append(extension)

        print(inspect.signature(extension.action))
        print("Signature", inspect.signature(extension))
        return self

    def execute(self):

        dependencies: dict[Type[Extension], list[ExtDependency]] = dict()

        # Collect the dependencies for each extension
        for ext in self.extensions:
            init_params = inspect.signature(ext.__init__).parameters

            ext_dependencies: list[ExtDependency] = []

            for param, signature in init_params.items():
                if param == "self":
                    continue

                annotation = signature.annotation

                if annotation is None:
                    raise RuntimeError(
                        f"The __init__ method of extension {ext} "
                        "needs type annotation on its parameters. "
                        "This is needed to properly inject the dependencies."
                    )

                ext_dependencies.append(
                    ExtDependency(param=param, annotation=annotation)
                )

            dependencies[ext] = ext_dependencies

        ext_to_execute = [ext for ext in self.extensions]
        data: dict[Any, Any] = dict()

        while len(ext_to_execute) > 0:
            has_executed = False

            for ext in ext_to_execute:
                missing_dependencies = [
                    dep
                    for dep in dependencies[ext]
                    if dep.annotation not in data.keys()
                ]

                if len(missing_dependencies) == 0:
                    dep_data = {
                        dep.param: data[dep.annotation] for dep in dependencies[ext]
                    }
                    data_annotation = inspect.signature(ext.action).return_annotation

                    if data_annotation is None:
                        raise RuntimeError(
                            f"Extension {ext} is missing the return type "
                            "annotation for the .action method"
                        )

                    ext_obj = ext(**dep_data)
                    data[data_annotation] = ext_obj.action()

                    has_executed = True
                    ext_to_execute = [ext2 for ext2 in ext_to_execute if ext != ext2]

            # Protection against infinite loops in case of circular dependencies
            if not has_executed:
                raise RuntimeError(
                    "The extensions could not be scheduled, "
                    f"{ext_to_execute} have unfulfilled dependencies"
                )
