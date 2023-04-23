"""Pricing examples from the Google Cloud Storage page.

See <https://cloud.google.com/storage/pricing-examples>.
"""
import sys

from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.network import network_package, NetworkData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = (
    Optimizer("google_cloud_storage", LpMinimize)
    .add_package(base_package)
    .add_package(performance_package)
    .add_package(network_package)
)


def simple_example() -> None:
    """Google Cloud Storage simple example."""
    print("Simple Example")

    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["my_bucket"],
            cloud_services=["cloud_storage_us_east1"],
            cr_to_cs_list={"my_bucket": ["cloud_storage_us_east1"]},
            cr_to_instance_demand={"my_bucket": 1},
            # The cost is entirely usage-based
            cs_to_base_cost={"cloud_storage_us_east1": 0},
        ),
        PerformanceData(
            performance_criteria=["data_storage", "data_processing_a", "data_processing_b"],
            performance_demand={
                # 50 GB
                ("my_bucket", "data_storage"): 50,
                # 10,000 class A operations
                ("my_bucket", "data_processing_a"): 10_000,
                # 50,000 class B operations
                ("my_bucket", "data_processing_b"): 50_000,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("cloud_storage_us_east1", "data_storage"): sys.maxsize,
                ("cloud_storage_us_east1", "data_processing_a"): sys.maxsize,
                ("cloud_storage_us_east1", "data_processing_b"): sys.maxsize,
            },
            cost_per_unit={
                # $0.020/GB
                ("cloud_storage_us_east1", "data_storage"): 0.020,
                # $0.005/1,000 operations
                ("cloud_storage_us_east1", "data_processing_a"): 0.005 / 1_000,
                # $0.0004/1,000 operations
                ("cloud_storage_us_east1", "data_processing_b"): 0.0004 / 1_000,
            },
        ),
        NetworkData(
            locations={"us_east1", "americas/emea"},
            cs_to_loc={"cloud_storage_us_east1": "us_east1"},
            loc_and_loc_to_cost={
                # $0.12/GB for egress traffic
                ("us_east1", "americas/emea"): 0.12,
                # Other traffic not relevant here, so we set it to 0
                ("americas/emea", "us_east1"): 0,
                ("americas/emea", "americas/emea"): 0,
                ("us_east1", "us_east1"): 0,
            },
            cr_and_loc_to_traffic={
                # 1GB egress traffic
                ("my_bucket", "americas/emea"): 1,
            },
            cr_and_loc_to_max_latency={},
            loc_and_loc_to_latency={
                # Latencies are not relevant here, so we set them to 0
                ("us_east1", "americas/emea"): 0,
                ("americas/emea", "us_east1"): 0,
                ("americas/emea", "americas/emea"): 0,
                ("us_east1", "us_east1"): 0,
            },
            # No traffic between CRs
            cr_and_cr_to_traffic={},
            cr_and_cr_to_max_latency={},
        )
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    print(f"- Total Charges: ${cost:.2f}")

    expected_cost = 1.19
    assert abs(cost - expected_cost) < 0.1, f"Got {cost:.2f}, expected {expected_cost:.2f}"


if __name__ == "__main__":
    simple_example()
