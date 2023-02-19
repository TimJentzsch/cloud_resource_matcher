from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Avoid circular imports
    from .validated_optimizer import ValidatedOptimizer


class BuiltOptimizer:
    validated_optimizer: ValidatedOptimizer
    build_data: dict[str, Any]

    def __init__(
        self, validated_optimizer: ValidatedOptimizer, build_data: dict[str, Any]
    ):
        self.validated_optimizer = validated_optimizer
        self.build_data = build_data

    def solve(self):
        # FIXME: Implement this
        pass
