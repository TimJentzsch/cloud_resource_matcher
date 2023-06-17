"""A small example, demonstrating the most basic features."""
from optiframe import InfeasibleError, Optimizer, SolutionObjValue
from pulp import LpMinimize

from cloud_resource_matcher.modules.base import BaseData, BaseSolution, base_module
from cloud_resource_matcher.modules.performance import PerformanceData, performance_module


def main() -> None:
    """Run the small demo example."""
    # Create the data for the problem instance
    base_data = BaseData(
        cloud_services=["engine_1", "engine_2", "storage_1", "storage_2"],
        cs_to_base_cost={
            "engine_1": 10,
            "engine_2": 20,
            "storage_1": 0,
            "storage_2": 40,
        },
        cloud_resources=["vm_1", "vm_2", "data_1"],
        cr_to_cs_list={
            "vm_1": ["engine_1", "engine_2"],
            "vm_2": ["engine_1", "engine_2"],
            "data_1": ["storage_1", "storage_2"],
        },
        cr_to_instance_demand={
            "vm_1": 2,
            "vm_2": 5,
            "data_1": 1,
        },
    )

    performance_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM", "storage"],
        performance_demand={
            # vm_1
            ("vm_1", "vCPUs"): 4,
            ("vm_1", "RAM"): 8,
            ("vm_1", "storage"): 0,
            # vm_2
            ("vm_2", "vCPUs"): 2,
            ("vm_2", "RAM"): 4,
            ("vm_2", "storage"): 0,
            # data_1
            ("data_1", "vCPUs"): 0,
            ("data_1", "RAM"): 0,
            ("data_1", "storage"): 250,
        },
        performance_supply={
            # engine_1
            ("engine_1", "vCPUs"): 4,
            ("engine_1", "RAM"): 4,
            ("engine_1", "storage"): 0,
            # engine_2
            ("engine_2", "vCPUs"): 8,
            ("engine_2", "RAM"): 16,
            ("engine_2", "storage"): 0,
            # storage_1
            ("storage_1", "vCPUs"): 0,
            ("storage_1", "RAM"): 0,
            ("storage_1", "storage"): 1_000,
            # storage_2
            ("storage_2", "vCPUs"): 0,
            ("storage_2", "RAM"): 0,
            ("storage_2", "storage"): 1_000,
        },
        cost_per_unit={
            ("storage_1", "storage"): 0.4,
            ("storage_2", "storage"): 0.2,
        },
    )

    optimizer = (
        # Create a new optimizer, minimizing the costs
        Optimizer("Small Demo", LpMinimize)
        # Add the needed modules to solve the problem
        .add_modules(base_module, performance_module)
        # Initialize the data of the problem instance
        .initialize(base_data, performance_data)
    )

    try:
        # Solve the problem
        solution_data = optimizer.solve()
    except InfeasibleError:
        print("The given problem is infeasible!")
        exit(1)

    # Extract the solution
    cost = solution_data[SolutionObjValue].objective_value
    base_solution: BaseSolution = solution_data[BaseSolution]

    print(f"Total cost: {cost:.2f}")
    print(f"Matching: {base_solution.cr_to_cs_matching}")


if __name__ == "__main__":
    main()
