from pulp import LpProblem, LpMinimize

from optimizer.optimizer_v2.extension import Extension


class CreateMipExt(Extension[LpProblem]):
    def __init__(self):
        pass

    def action(self) -> LpProblem:
        return LpProblem("cloud_cost_optimization", LpMinimize)
