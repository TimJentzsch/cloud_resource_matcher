from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .built_optimizer import BuiltOptimizer
from ..extensions.decorators import DependencyInfo

if TYPE_CHECKING:
    # Avoid circular imports
    from .optimizer import Optimizer


class ValidatedOptimizer:
    optimizer: Optimizer

    def __init__(self, optimizer: Optimizer):
        self.optimizer = optimizer

    def build_mip(self):
        mip_info: dict[str, DependencyInfo] = {
            e_id: extension.extend_mip()
            for e_id, extension in self.optimizer.extensions.items()
        }

        dependencies: dict[str, set[str]] = {
            e_id: info.dependencies for e_id, info in mip_info.items()
        }

        to_build: dict[str, set[str]] = {**dependencies}

        build_data: dict[str, Any] = dict()

        while len(to_build.keys()) > 0:
            # If an extension has no outstanding dependencies it can be built
            can_be_built = [e_id for e_id, deps in to_build.items() if len(deps) == 0]

            assert (
                len(can_be_built) > 0
            ), "Extensions can't be scheduled, dependency cycle detected"

            # Validate the extensions and add them to the validated data
            for e_id in can_be_built:
                info = mip_info[e_id]
                dependency_data = {
                    dep: self.optimizer.data[dep] for dep in info.dependencies
                }

                build_data[e_id] = mip_info[e_id].action_fn(
                    data=self.optimizer.data[e_id], **dependency_data
                )

            # Update the extensions that need to be built
            to_build = {
                e_id: set(dep for dep in deps if dep not in can_be_built)
                for e_id, deps in to_build.items()
                if e_id not in can_be_built
            }

        return BuiltOptimizer(validated_optimizer=self, build_data=build_data)
