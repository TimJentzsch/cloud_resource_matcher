from enum import Enum


class Solver(Enum):
    CBC = 0
    GUROBI = 1
    SCIP = 2
