from dataclasses import dataclass
from typing import Callable

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
        def inner():
            return DependencyInfo(dependencies=set(*deps), action_fn=action_fn)

        return inner

    return decorator
