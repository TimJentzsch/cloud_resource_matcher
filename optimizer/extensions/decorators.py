from dataclasses import dataclass
from typing import Callable, Any


ValidateFn = Callable[[...], Any]


@dataclass
class ValidationInfo:
    # The IDs of the extensions whose data is needed for validation
    dependencies: set[str]

    validate_fn: ValidateFn


def validate_dependencies(
    *dependencies: str,
) -> Callable[[Callable], Callable[[], ValidationInfo]]:
    def decorator(validate_fn: Callable) -> Callable[[], ValidationInfo]:
        def inner():
            return ValidationInfo(
                dependencies=set(*dependencies), validate_fn=validate_fn
            )

        return inner

    return decorator
