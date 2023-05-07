"""Benchmarks for a model containing all modules."""
from typing import Any

from optiframe import Optimizer
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize

from benches.utils import setup_benchmark
from benches.utils.data_generation import generate_base_data, generate_network_data
from cloud_resource_matcher.modules.base import base_module
from cloud_resource_matcher.modules.multi_cloud import MultiCloudData, multi_cloud_module
from cloud_resource_matcher.modules.network import network_module
from cloud_resource_matcher.modules.performance import PerformanceData, performance_module
from cloud_resource_matcher.modules.service_limits import ServiceLimitsData, service_limits_module

DEFAULT_PARAMS = {
    "cr_count": 500,
    "cs_count": 500,
    "cs_count_per_cr": 200,
    "csp_count": 3,
    "loc_count": 500,
    "cr_to_loc_connections": 40,
    "cr_to_cr_connections": 10,
}


def bench() -> None:
    """Run the benchmarks for the complete model."""
    print("\n\n=== CR_TO_CR_CONNECTIONS ===")
    bench_cr_to_cr_connections()

    print("\n\n=== CR_COUNT ===")
    bench_cr_count()

    print("\n\n=== CS_COUNT ===")
    bench_cs_count()

    print("\n\n=== CS_COUNT_PER_CR ===")
    bench_cs_count_per_cr()

    print("\n\n=== CSP_COUNT ===")
    bench_csp_count()

    print("\n\n=== LOC_COUNT ===")
    bench_loc_count()

    print("\n\n=== CR_TO_LOC_CONNECTIONS ===")
    bench_cr_to_loc_connections()


def bench_cr_count() -> None:
    """Run benchmarks varying the number of cloud resources."""
    setup_benchmark(
        "cloud resource count",
        "cr_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count() -> None:
    """Run benchmarks varying the number of cloud services."""
    setup_benchmark(
        "cloud service count",
        "cs_count",
        [200, 300, 400, 500, 600, 700, 800, 900, 1000],
        {**DEFAULT_PARAMS},
        get_optimizer_fn=get_optimizer,
    )


def bench_cs_count_per_cr() -> None:
    """Run benchmarks varying the number of applicable CSs for a CR."""
    setup_benchmark(
        "count of applicable cloud services per cloud resource",
        "cs_count_per_cr",
        [50, 100, 150, 200, 250, 300, 350, 400],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_csp_count() -> None:
    """Run benchmarks varying the number of cloud service providers."""
    setup_benchmark(
        "cloud service provider count",
        "csp_count",
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_loc_count() -> None:
    """Run benchmarks varying the number of network locations."""
    setup_benchmark(
        "network location count",
        "loc_count",
        [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_cr_to_loc_connections() -> None:
    """Run benchmarks varying the number of connections between a CR and a location."""
    setup_benchmark(
        "count of connections between CR and a network location",
        "cr_to_loc_connections",
        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def bench_cr_to_cr_connections() -> None:
    """Run benchmarks varying the number of connections between CR pairs."""
    setup_benchmark(
        "count of connections between CR pairs",
        "cr_to_cr_connections",
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36],
        DEFAULT_PARAMS,
        get_optimizer_fn=get_optimizer,
    )


def get_optimizer(params: dict[str, Any]) -> InitializedOptimizer:
    """Get an optimizer instance for the provided parameters."""
    cr_count = params["cr_count"]
    cs_count = params["cs_count"]
    cs_count_per_cr = params["cs_count_per_cr"]
    csp_count = params["csp_count"]
    loc_count = params["loc_count"]
    cr_to_loc_connections = params["cr_to_loc_connections"]
    cr_to_cr_connections = params["cr_to_cr_connections"]

    base_data = generate_base_data(cr_count, cs_count, cs_count_per_cr)

    performance_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM"],
        performance_demand={
            **{(f"cr_{cr}", "vCPUs"): cr % 5 for cr in range(cr_count)},
            **{(f"cr_{cr}", "RAM"): (cr + cr * 3 + 25) % 64 for cr in range(cr_count)},
        },
        # Set high to avoid CS to be filtered out durin pre-processing
        performance_supply={
            **{(f"cs_{cs}", "vCPUs"): 1000 for cs in range(cs_count)},
            **{(f"cs_{cs}", "RAM"): 1000 for cs in range(cs_count)},
        },
        cost_per_unit={
            **{(f"cs_{cs}", "vCPUs"): (cs * 9) % 20 + 3 for cs in range(cs_count)},
            **{(f"cs_{cs}", "RAM"): (cs * cs + 4 * cs) % 10 + 2 for cs in range(cs_count)},
        },
    )

    multi_data = MultiCloudData(
        cloud_service_providers=[f"csp_{csp}" for csp in range(csp_count)],
        csp_to_cs_list={
            f"csp_{csp}": [f"cs_{cs}" for cs in range(cs_count) if cs % csp_count == csp]
            for csp in range(csp_count)
        },
        min_csp_count=1,
        max_csp_count=3,
        csp_to_cost={f"csp_{csp}": csp * 10_000 for csp in range(csp_count)},
    )

    network_data = generate_network_data(
        cr_count, cs_count, loc_count, cr_to_loc_connections, cr_to_cr_connections
    )

    service_limits_data = ServiceLimitsData(
        cr_to_max_instance_demand={
            f"cr_{cr}": min(base_data.cr_to_instance_demand[f"cr_{cr}"], 3 + cr % 20)
            for cr in range(cr_count)
        },
        cs_to_instance_limit={f"cs_{cs}": 40 + cs * 3 for cs in range(cs_count)},
    )

    return (
        Optimizer("bench_complete", sense=LpMinimize)
        .add_modules(
            base_module,
            performance_module,
            network_module,
            multi_cloud_module,
            service_limits_module,
        )
        .initialize(base_data, performance_data, network_data, multi_data, service_limits_data)
    )
