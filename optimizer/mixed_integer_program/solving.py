from dataclasses import dataclass
from enum import Enum

from optimizer.mixed_integer_program.types import (
    VmServiceMatching,
    ServiceInstanceCount,
)
from optimizer.optimizer_toolbox_model.data import Cost


@dataclass
class SolveSolution:
    vm_service_matching: VmServiceMatching
    service_instance_count: ServiceInstanceCount
    cost: Cost


class SolveErrorReason(Enum):
    INFEASIBLE = 0


class SolveError(RuntimeError):
    reason: SolveErrorReason

    def __init__(self, reason: SolveErrorReason):
        super().__init__(f"Could not solve optimization problem: {reason}")
        self.reason = reason
