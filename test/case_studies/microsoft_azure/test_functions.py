"""Pricing examples from the Azure Functions pricing page.

See <https://azure.microsoft.com/en-us/pricing/details/functions/>.
"""
import sys

import pytest
from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from cloud_resource_matcher.modules.base import base_module, BaseData
from cloud_resource_matcher.modules.performance import performance_module, PerformanceData

OPTIMIZER = Optimizer("azure_functions", LpMinimize).add_modules(base_module, performance_module)


@pytest.mark.skip("Free grants can't be represented yet")
def test_example() -> None:
    """Azure Functions pricing example."""
    solution = OPTIMIZER.initialize(
        BaseData(
            cloud_resources=["workload"],
            cloud_services=["azure_functions"],
            cr_to_cs_list={"workload": ["azure_functions"]},
            # 3 million executions
            cr_to_instance_demand={"workload": 3_000_000},
            # The cost is entirely usage-based
            cs_to_base_cost={"azure_functions": 0},
        ),
        PerformanceData(
            performance_criteria=["resource_consumption", "executions"],
            performance_demand={
                # 1 second * 512 MB / 1,024 MB/GB
                ("workload", "resource_consumption"): 1 * 512 / 1_024,
                # 1 execution per request
                ("workload", "executions"): 1,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("azure_functions", "resource_consumption"): sys.maxsize,
                ("azure_functions", "executions"): sys.maxsize,
            },
            cost_per_unit={
                # $0.000016/GB-s
                ("azure_functions", "resource_consumption"): 0.000016,
                # $0.20/million executions
                ("azure_functions", "executions"): 0.20 / 1_000_000,
            },
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    assert cost == pytest.approx(18.00, 0.01)
