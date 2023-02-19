from typing import Self, Any

from optimizer.extensions.decorators import DependencyInfo
from optimizer.extensions.extension import Extension, ExtensionId
from optimizer.optimizer.validated_optimizer import ValidatedOptimizer


class Optimizer:
    extensions: dict[ExtensionId, Extension]
    data: dict[str, Any]

    def __init__(self):
        self.extensions = dict()

    def register_extension(self, extension: Extension) -> Self:
        """Register a new extension."""
        e_id = extension.identifier()
        self.extensions[e_id] = extension

        return self

    def add_data(self, e_id: ExtensionId, data: Any) -> Self:
        """Add the data for an extension with the given ID."""
        assert (
            e_id in self.extensions.keys()
        ), f"Extension {e_id} is not registered yet, use `.register_extension` first."

        self.data[e_id] = data
        return self

    def validate(self) -> ValidatedOptimizer:
        validation_info: dict[ExtensionId, DependencyInfo] = {
            e_id: extension.validate() for e_id, extension in self.extensions.items()
        }

        dependencies: dict[ExtensionId, set[ExtensionId]] = {
            e_id: info.dependencies for e_id, info in validation_info.items()
        }

        to_validate: dict[ExtensionId, set[ExtensionId]] = {**dependencies}

        while len(to_validate.keys()) > 0:
            # If an extension has no outstanding dependencies it can be validated
            can_be_validated = [
                e_id for e_id, deps in to_validate.items() if len(deps) == 0
            ]

            assert (
                len(can_be_validated) > 0
            ), "Extensions can't be scheduled, dependency cycle detected"

            # Validate the extensions and add them to the validated data
            for e_id in can_be_validated:
                info = validation_info[e_id]
                dependency_data = {dep: self.data[dep] for dep in info.dependencies}

                validation_info[e_id].action_fn(data=self.data[e_id], **dependency_data)

            # Update the extensions that need to be validated
            to_validate = {
                e_id: set(dep for dep in deps if dep not in can_be_validated)
                for e_id, deps in to_validate.items()
                if e_id not in can_be_validated
            }

        return ValidatedOptimizer(optimizer=self)
