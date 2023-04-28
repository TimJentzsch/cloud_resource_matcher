"""Pricing examples from the Google Cloud Storage page.

See <https://cloud.google.com/storage/pricing-examples>.
"""
import sys
from itertools import product

import pytest
from optiframe import Optimizer, SolutionObjValue
from pulp import LpMinimize, pulp

from cloud_resource_matcher.modules.base import base_module, BaseData
from cloud_resource_matcher.modules.network import network_module, NetworkData
from cloud_resource_matcher.modules.performance import performance_module, PerformanceData

OPTIMIZER = Optimizer("google_cloud_storage", LpMinimize).add_modules(
    base_module, performance_module, network_module
)


TB_TO_GB = 1_024


def test_simple_example() -> None:
    """Google Cloud Storage simple example."""
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
            locations={"us_east1", "americas_emea"},
            cs_to_loc={"cloud_storage_us_east1": "us_east1"},
            loc_and_loc_to_cost={
                # $0.12/GB for egress traffic
                ("us_east1", "americas_emea"): 0.12,
                # Other traffic not relevant here, so we set it to 0
                ("americas_emea", "us_east1"): 0,
                ("americas_emea", "americas_emea"): 0,
                ("us_east1", "us_east1"): 0,
            },
            cr_and_loc_to_traffic={
                # 1GB egress traffic
                ("my_bucket", "americas_emea"): 1,
            },
            cr_and_loc_to_max_latency={},
            loc_and_loc_to_latency={
                # Latencies are not relevant here, so we set them to 0
                ("us_east1", "americas_emea"): 0,
                ("americas_emea", "us_east1"): 0,
                ("americas_emea", "americas_emea"): 0,
                ("us_east1", "us_east1"): 0,
            },
            # No traffic between CRs
            cr_and_cr_to_traffic={},
            cr_and_cr_to_max_latency={},
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value
    print(f"- Total Charges: ${cost:.2f}")

    expected_cost = 1.19
    assert abs(cost - expected_cost) < 0.1, f"Got {cost:.2f}, expected {expected_cost:.2f}"


def test_detailed_example() -> None:
    """Google Cloud Storage detailed example."""
    locations = {
        "us_east1",
        # Pricing tiers modeled as separate locations
        "americas_emea_t1",
        "americas_emea_t2",
        "americas_emea_t3",
        "asia_pacific_t1",
        "asia_pacific_t2",
        "asia_pacific_t3",
    }

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
            performance_criteria=[
                "standard_storage_multi_region",
                "standard_storage_nam4_dual_region",
                "nearline_storage_multi_region",
                "class_a_operations_standard_storage",
                "class_b_operations_standard_storage",
                "class_b_operations_nearline_storage",
                "data_retrieval",
                "turbo_replication",
            ],
            performance_demand={
                # 60 TB Standard storage in a multi-region
                ("my_bucket", "standard_storage_multi_region"): 60 * TB_TO_GB,
                # 30 TB Standard storage in the nam4 dual-region
                ("my_bucket", "standard_storage_nam4_dual_region"): 30 * TB_TO_GB,
                # 100 TB Nearline storage in a multi-region
                ("my_bucket", "nearline_storage_multi_region"): 100 * TB_TO_GB,
                # 100,000 Class A operations (object adds, bucket and object listings)
                # on Standard storage data
                ("my_bucket", "class_a_operations_standard_storage"): 100_000,
                # 10,000,000 Class B operations (object gets, retrieving bucket and object metadata)
                # on Standard storage data
                ("my_bucket", "class_b_operations_standard_storage"): 10_000_000,
                # 1,000,000 Class B operations (object gets, retrieving bucket and object metadata)
                # on Nearline storage data
                ("my_bucket", "class_b_operations_nearline_storage"): 1_000_000,
                # 10 TB Data retrieval (the Nearline storage portion of your overall data egress)
                ("my_bucket", "data_retrieval"): 10 * TB_TO_GB,
                # 14 TB inter-region replication in a dual-region (turbo replication)
                # This should be 14,336 GB, but in their example they use 14,485 GB
                ("my_bucket", "turbo_replication"): 14_485,
            },
            # Available resources virtually unbounded
            performance_supply={
                ("cloud_storage_us_east1", "standard_storage_multi_region"): sys.maxsize,
                ("cloud_storage_us_east1", "standard_storage_nam4_dual_region"): sys.maxsize,
                ("cloud_storage_us_east1", "nearline_storage_multi_region"): sys.maxsize,
                ("cloud_storage_us_east1", "class_a_operations_standard_storage"): sys.maxsize,
                ("cloud_storage_us_east1", "class_b_operations_standard_storage"): sys.maxsize,
                ("cloud_storage_us_east1", "class_b_operations_nearline_storage"): sys.maxsize,
                ("cloud_storage_us_east1", "data_retrieval"): sys.maxsize,
                ("cloud_storage_us_east1", "turbo_replication"): sys.maxsize,
            },
            cost_per_unit={
                # $0.026 per GB
                ("cloud_storage_us_east1", "standard_storage_multi_region"): 0.026,
                # $0.044 per GB
                ("cloud_storage_us_east1", "standard_storage_nam4_dual_region"): 0.044,
                # $0.015 per GB
                ("cloud_storage_us_east1", "nearline_storage_multi_region"): 0.015,
                # $0.01 per 1,000 operations
                ("cloud_storage_us_east1", "class_a_operations_standard_storage"): 0.01 / 1_000,
                # $0.0004 per 1,000 operations
                ("cloud_storage_us_east1", "class_b_operations_standard_storage"): 0.0004 / 1_000,
                # $0.001 per 1,000 operations
                ("cloud_storage_us_east1", "class_b_operations_nearline_storage"): 0.001 / 1_000,
                # 0.01 per GB
                ("cloud_storage_us_east1", "data_retrieval"): 0.01,
                # $0.04 per GB
                ("cloud_storage_us_east1", "turbo_replication"): 0.04,
            },
        ),
        NetworkData(
            locations=locations,
            cs_to_loc={"cloud_storage_us_east1": "us_east1"},
            loc_and_loc_to_cost={
                # We don't care about most costs
                **{(loc1, loc2): 0 for loc1, loc2 in product(locations, repeat=2)},
                # 0-1 TB tier for Americas and EMEA: $0.12/GB
                ("us_east1", "americas_emea_t1"): 0.12,
                # 1-10 TB tier for Americas and EMEA: $0.11/GB
                ("us_east1", "americas_emea_t2"): 0.11,
                # 10+ TB tier for Americas and EMEA: $0.08/GB
                ("us_east1", "americas_emea_t3"): 0.08,
                # 0-1 TB tier for Asia-Pacific: $0.12/GB
                ("us_east1", "asia_pacific_t1"): 0.12,
                # 1-10 TB tier for Asia-Pacific: $0.11/GB
                ("us_east1", "asia_pacific_t2"): 0.11,
                # 10+ TB tier for Asia-Pacific: $0.08/GB
                ("us_east1", "asia_pacific_t3"): 0.08,
            },
            cr_and_loc_to_traffic={
                # 0-1 TB tier for Americas and EMEA: 1 TB
                ("my_bucket", "americas_emea_t1"): 1 * TB_TO_GB,
                # 1-10 TB tier for Americas and EMEA: 9 TB
                ("my_bucket", "americas_emea_t2"): 9 * TB_TO_GB,
                # 10+ TB tier for Americas and EMEA: 15 TB
                ("my_bucket", "americas_emea_t3"): 15 * TB_TO_GB,
                # 0-1 TB tier for Asia-Pacific: 1 TB
                ("my_bucket", "asia_pacific_t1"): 1 * TB_TO_GB,
                # 1-10 TB tier for Asia-Pacific: 9 TB
                ("my_bucket", "asia_pacific_t2"): 9 * TB_TO_GB,
                # 10+ TB tier for Asia-Pacific: 15 TB
                ("my_bucket", "asia_pacific_t3"): 15 * TB_TO_GB,
            },
            cr_and_loc_to_max_latency={},
            loc_and_loc_to_latency={
                # Latencies are not relevant here, so we set them to 0
                **{(loc1, loc2): 0 for loc1, loc2 in product(locations, repeat=2)},
            },
            # No traffic between CRs
            cr_and_cr_to_traffic={},
            cr_and_cr_to_max_latency={},
        ),
    ).solve(pulp.PULP_CBC_CMD(msg=False))

    cost = solution[SolutionObjValue].objective_value

    # The example shows a total of $9,893.80, but the sum of the components is $9,903.80
    assert cost == pytest.approx(9903.80, 0.01)
