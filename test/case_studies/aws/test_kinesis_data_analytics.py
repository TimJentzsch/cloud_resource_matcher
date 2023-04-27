"""Pricing examples from the Amazon Kinesis Data Analytics pricing page.

See <https://aws.amazon.com/kinesis/data-analytics/pricing/#Pricing_examples>.
"""
import sys

import pytest
from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from optimizer.packages.base import base_package, BaseData
from optimizer.packages.performance import performance_package, PerformanceData

OPTIMIZER = Optimizer("amazon_kinesis_data_analytics", LpMinimize).add_modules(
    base_package, performance_package
)


def test_pricing_example_1() -> None:
    """Studio Notebook with a Simple Streaming Filter"""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["studio_notebook"],
            cloud_services=["kinesis_analytics_us_east"],
            cr_to_cs_list={"studio_notebook": ["kinesis_analytics_us_east"]},
            # 30 Days * 24 Hours
            cr_to_instance_demand={"studio_notebook": 30 * 24},
            # The cost is entirely usage-based
            cs_to_base_cost={"kinesis_analytics_us_east": 0},
        ),
        PerformanceData(
            performance_criteria=["KPU", "running_application_storage"],
            performance_demand={
                # 4 KPUs + 2 for notebook
                ("studio_notebook", "KPU"): 4 + 2,
                # 4 KPUs * 50GB storage
                ("studio_notebook", "running_application_storage"): 4 * 50,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("kinesis_analytics_us_east", "KPU"): sys.maxsize,
                ("kinesis_analytics_us_east", "running_application_storage"): sys.maxsize,
            },
            cost_per_unit={
                # $0.11/Hour
                ("kinesis_analytics_us_east", "KPU"): 0.11,
                # $0.10/GB/month
                ("kinesis_analytics_us_east", "running_application_storage"): 0.10 / (30 * 24),
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(495.20, 0.01)


def test_pricing_example_2() -> None:
    """Studio Notebook with a Sliding Window Deployed to Streaming Mode"""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["studio_notebook_dev", "studio_notebook_prod", "backup"],
            cloud_services=["kinesis_analytics_us_east"],
            cr_to_cs_list={
                "studio_notebook_dev": ["kinesis_analytics_us_east"],
                "studio_notebook_prod": ["kinesis_analytics_us_east"],
                "backup": ["kinesis_analytics_us_east"],
            },
            cr_to_instance_demand={
                # 2 Days * 8 Hours
                "studio_notebook_dev": 2 * 8,
                # 28 Days * 24 Hours
                "studio_notebook_prod": 28 * 24,
                # 28 Days * 1 Backup
                "backup": 28,
            },
            # The cost is entirely usage-based
            cs_to_base_cost={"kinesis_analytics_us_east": 0},
        ),
        PerformanceData(
            performance_criteria=[
                "KPU",
                "running_application_storage",
                "durable_application_storage",
            ],
            performance_demand={
                # Dev: 4 KPUs + 2 for notebook
                ("studio_notebook_dev", "KPU"): 4 + 2,
                # Dev: 4 KPUs * 50GB storage
                ("studio_notebook_dev", "running_application_storage"): 4 * 50,
                # Prod: 2 KPUs + 1 for streaming
                ("studio_notebook_prod", "KPU"): 2 + 1,
                # Prod: 2 KPUs * 50GB storage
                ("studio_notebook_prod", "running_application_storage"): 2 * 50,
                # Backup: 1 MB * 1 GB/1,000MB
                ("backup", "durable_application_storage"): 1 / 1000,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("kinesis_analytics_us_east", "KPU"): sys.maxsize,
                ("kinesis_analytics_us_east", "running_application_storage"): sys.maxsize,
                ("kinesis_analytics_us_east", "durable_application_storage"): sys.maxsize,
            },
            cost_per_unit={
                # $0.11/Hour
                ("kinesis_analytics_us_east", "KPU"): 0.11,
                # $0.10/GB/month
                ("kinesis_analytics_us_east", "running_application_storage"): 0.10 / (30 * 24),
                # $0.023/GB/month
                ("kinesis_analytics_us_east", "durable_application_storage"): 0.023 / (30 * 24),
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(242.10, 0.01)
