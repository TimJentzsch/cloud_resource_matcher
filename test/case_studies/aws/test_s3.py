"""Pricing examples from the Amazon S3 Billing FAQ.

See <https://aws.amazon.com/s3/faqs/#Billing>.
"""
import sys

import pytest
from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = (
    Optimizer("amazon_s3", LpMinimize).add_package(base_package).add_package(performance_package)
)


GB_TO_BYTES = 1_073_741_824
TB_TO_BYTES = 1_024 * GB_TO_BYTES


def test_storage_example() -> None:
    """Amazon S3 storage pricing example."""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["data"],
            cloud_services=["amazon_s3"],
            cr_to_cs_list={"data": ["amazon_s3"]},
            cr_to_instance_demand={"data": 1},
            # The cost is entirely usage-based
            cs_to_base_cost={"amazon_s3": 0},
        ),
        PerformanceData(
            performance_criteria=["storage"],
            performance_demand={
                # 100 GB for 15 days, 100 TB for 16 days; converted Byte-Hours, then to GB-Months
                ("data", "storage"): (100 * GB_TO_BYTES * 15 * 24 + 100 * TB_TO_BYTES * 16 * 24)
                // GB_TO_BYTES
                // 744
            },
            # Available resources virtually unbounded
            performance_supply={
                ("amazon_s3", "storage"): sys.maxsize,
            },
            cost_per_unit={
                # Tiered pricing is not possible yet
                # Estimate cost by choosing price of 0TB to 50TB pricing
                ("amazon_s3", "storage"): 0.023,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(1_215.00, 0.01)
