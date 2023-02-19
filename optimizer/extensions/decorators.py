from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import errors
    from .extension import ExtensionId


@dataclass
class DependencyInfo:
    # The IDs of the extensions whose data is needed for the action
    dependencies: set[ExtensionId]

    # The action to execute, with the injected dependencies
    action_fn: Callable


def dependencies(
    *deps: str,
) -> Callable[[Callable], Callable[[], DependencyInfo]]:
    def decorator(action_fn: Callable) -> Callable[[], DependencyInfo]:
        def inner(self):
            return DependencyInfo(dependencies=set(deps), action_fn=lambda: action_fn(self))

        return inner

    return decorator
