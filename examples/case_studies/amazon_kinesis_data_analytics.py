"""The examples from the Amazon Kinesis Data Analytics pricing page.

See <https://aws.amazon.com/kinesis/data-analytics/pricing/#Pricing_examples>.
"""
import sys

from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = (
    Optimizer("amazon_kinesis_data_analytics", LpMinimize)
    .add_package(base_package)
    .add_package(performance_package)
)


def pricing_example_1() -> None:
    print("PRICING EXAMPLE 1")

    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["studio_notebook"],
            cloud_services=["kinesis_analytics_us_east"],
            cr_to_cs_list={"studio_notebook": ["kinesis_analytics_us_east"]},
            cr_to_instance_demand={"studio_notebook": 1},
            # The cost is entirely usage-based
            cs_to_base_cost={"kinesis_analytics_us_east": 0},
        ),
        PerformanceData(
            performance_criteria=["KPU_compute", "KPU_storage"],
            performance_demand={
                # 30 Days * 24 Hours * (4 KPUs + 2 extra for notebook application)
                ("studio_notebook", "KPU_compute"): 30 * 24 * (4 + 2),
                # 4 KPUs * 50GB storage
                ("studio_notebook", "KPU_storage"): 4 * 50,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("kinesis_analytics_us_east", "KPU_compute"): sys.maxsize,
                ("kinesis_analytics_us_east", "KPU_storage"): sys.maxsize,
            },
            cost_per_unit={
                # $0.11/Hour
                ("kinesis_analytics_us_east", "KPU_compute"): 0.11,
                # $0.10/GB/month
                ("kinesis_analytics_us_east", "KPU_storage"): 0.10,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == 495.20

    print(f"- Total Charges: ${cost:.2f}")


if __name__ == "__main__":
    pricing_example_1()
