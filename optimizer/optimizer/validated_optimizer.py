from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pulp import LpProblem, LpMinimize, LpAffineExpression

from .built_optimizer import BuiltOptimizer
from optimizer.extensions.decorators import DependencyInfo
from optimizer.extensions.extension import ExtensionId

if TYPE_CHECKING:
    # Avoid circular imports
    from .optimizer import Optimizer


class ValidatedOptimizer:
    optimizer: Optimizer

    def __init__(self, optimizer: Optimizer):
        self.optimizer = optimizer

    def build_mip(self):
        problem = LpProblem("cloud_cost_optimization", LpMinimize)
        objective = LpAffineExpression()

        mip_info: dict[ExtensionId, DependencyInfo] = {
            e_id: extension.extend_mip()
            for e_id, extension in self.optimizer.extensions.items()
        }

        dependencies: dict[ExtensionId, set[ExtensionId]] = {
            e_id: info.dependencies for e_id, info in mip_info.items()
        }

        to_build: dict[ExtensionId, set[ExtensionId]] = {**dependencies}

        mip_data: dict[ExtensionId, Any] = dict()

        while len(to_build.keys()) > 0:
            # If an extension has no outstanding dependencies it can be built
            can_be_built = [e_id for e_id, deps in to_build.items() if len(deps) == 0]

            assert (
                len(can_be_built) > 0
            ), "Extensions can't be scheduled, dependency cycle detected"

            # Extend the MIP with extensions and add the result to the build data
            for e_id in can_be_built:
                info = mip_info[e_id]
                dependency_data = {dep: mip_data[dep] for dep in info.dependencies}

                mip_data[e_id] = mip_info[e_id].action_fn(
                    problem=problem,
                    objective=objective,
                    data=self.optimizer.data[e_id],
                    **dependency_data,
                )

            # Update the extensions that need to be built
            to_build = {
                e_id: set(dep for dep in deps if dep not in can_be_built)
                for e_id, deps in to_build.items()
                if e_id not in can_be_built
            }

        # Update the objective
        problem.setObjective(objective)

        return BuiltOptimizer(
            validated_optimizer=self, problem=problem, mip_data=mip_data
        )
