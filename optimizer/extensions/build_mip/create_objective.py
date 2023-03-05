from pulp import LpAffineExpression

from optimizer.optimizer.extension import Extension


class CreateObjectiveExt(Extension[LpAffineExpression]):
    def __init__(self):
        pass

    def action(self) -> LpAffineExpression:
        return LpAffineExpression()
