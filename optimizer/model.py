from typing import Dict

from pulp import LpVariable, LpProblem, LpMinimize, lpSum

from optimizer.data import Data, VirtualMachine, Service


class Model:
    """The model for the cloud computing cost optimization problem."""
    data: Data
    prob: LpProblem
    x: Dict[(VirtualMachine, Service)]

    def __init__(self, data: Data):
        """Create a new model for the cost optimization problem."""
        self.data = data
        self.prob = LpProblem("cloud_cost_optimization", LpMinimize)

        # == Variables ==

        # Assign virtual machine v to cloud service s?
        self.x = {
            (v, s): LpVariable(f"x_(v,s)")
            for v in data.virtual_machines
            for s in data.services
        }

        # == Constraints ==

        # Assign each VM to exactly one cloud service
        for v in data.virtual_machines:
            self.prob += lpSum(self.x[v, s] for s in data.services) == 1

        # == Objective ==

        # Minimize costs
        self.prob += lpSum(
            self.x[v, s] * data.service_base_costs[s]
            for v in data.virtual_machines
            for s in data.services
        )

    def solve(self) -> LpProblem:
        """Solve the optimization problem."""
        self.prob.solve()
        return self.prob
