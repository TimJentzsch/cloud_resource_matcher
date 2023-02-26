from pulp import LpProblem, LpMinimize, LpAffineExpression

from optimizer.optimizer_v2.extension import Extension


class CreateObjectiveExt(Extension[LpAffineExpression]):
    def __init__(self):
        pass

    def action(self) -> LpAffineExpression:
        return LpAffineExpression()
