"""The examples from the Amazon Aurora pricing page.

See <https://aws.amazon.com/rds/aurora/pricing/>.
"""
import sys

from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = (
    Optimizer("amazon_aurora", LpMinimize)
    .add_package(base_package)
    .add_package(performance_package)
)


def database_storage_and_ios() -> None:
    """Database Storage and I/Os."""
    print("Database Storage and I/Os")

    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["database"],
            cloud_services=["amazon_aurora"],
            cr_to_cs_list={"database": ["amazon_aurora"]},
            cr_to_instance_demand={"database": 1},
            # The cost is entirely usage-based
            cs_to_base_cost={"amazon_aurora": 0},
        ),
        PerformanceData(
            performance_criteria=["storage", "i/o"],
            performance_demand={
                # Starting at 1,000 GB, growing 20 GB daily, 30 days
                ("database", "storage"): (1000 * 30 + sum(i * 20 for i in range(30))) / 30,
                # 100 reads per second + 10 writes per second
                # 730 hours * 60 minutes * 60 seconds
                ("database", "i/o"): (100 + 10) * 730 * 60 * 60,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("amazon_aurora", "storage"): sys.maxsize,
                ("amazon_aurora", "i/o"): sys.maxsize,
            },
            cost_per_unit={
                # $0.10/GB-month
                ("amazon_aurora", "storage"): 0.10,
                # $0.20/million requests
                ("amazon_aurora", "i/o"): 0.20 / 1_000_000,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    print(f"- Total Charges: ${cost:.2f}")

    expected_cost = 129.00 + 57.80
    assert abs(cost - expected_cost) < 0.1, f"Got {cost:.2f}, expected {expected_cost:.2f}"


if __name__ == "__main__":
    database_storage_and_ios()
