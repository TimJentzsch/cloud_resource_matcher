"""Pricing examples from the AWS Lambda pricing page.

See <https://aws.amazon.com/lambda/pricing/>.
"""
import sys

import pytest
from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = Optimizer("aws_lambda", LpMinimize).add_modules(base_package, performance_package)


@pytest.mark.skip("400,000 GB-s included in free tier not handled yet")
def test_ephemeral_storage_pricing_example_1() -> None:
    """Mobile application backend."""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["food_order"],
            cloud_services=["aws_lambda_us_east"],
            cr_to_cs_list={"food_order": ["aws_lambda_us_east"]},
            # 3 million requests
            cr_to_instance_demand={"food_order": 3_000_000},
            # The cost is entirely usage-based
            cs_to_base_cost={"aws_lambda_us_east": 0},
        ),
        PerformanceData(
            performance_criteria=["compute", "requests"],
            performance_demand={
                # 0.120s * 1536MB/1024MB
                ("food_order", "compute"): 0.120 * (1536 / 1024),
                # 1 request per message
                ("food_order", "requests"): 1,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("aws_lambda_us_east", "requests"): sys.maxsize,
                ("aws_lambda_us_east", "compute"): sys.maxsize,
            },
            cost_per_unit={
                # $0.20/million
                ("aws_lambda_us_east", "requests"): 0.20 / 1_000_000,
                # $0.0000166667/GB-s
                ("aws_lambda_us_east", "compute"): 0.0000166667,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(2.73, 0.01)


def test_ephemeral_storage_pricing_example_2() -> None:
    """Enriching streaming telemetry with additional metadata."""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["telemetry_metadata"],
            cloud_services=["aws_lambda_us_east"],
            cr_to_cs_list={"telemetry_metadata": ["aws_lambda_us_east"]},
            # 10,000 vehicles * 24 hours * 31 days
            cr_to_instance_demand={"telemetry_metadata": 10_000 * 24 * 31},
            # The cost is entirely usage-based
            cs_to_base_cost={"aws_lambda_us_east": 0},
        ),
        PerformanceData(
            performance_criteria=["requests", "compute"],
            performance_demand={
                # 1 request per message
                ("telemetry_metadata", "requests"): 1,
                # 2 seconds * 1GB
                ("telemetry_metadata", "compute"): 2 * 1,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("aws_lambda_us_east", "requests"): sys.maxsize,
                ("aws_lambda_us_east", "compute"): sys.maxsize,
            },
            cost_per_unit={
                # $0.20/million
                ("aws_lambda_us_east", "requests"): 0.20 / 1_000_000,
                # $0.0000166667/GB-s
                ("aws_lambda_us_east", "compute"): 0.0000166667,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(249.49, 0.01)
