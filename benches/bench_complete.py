from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result, generate_base_data, generate_network_data
from optimizer.packages.base import base_package
from optimizer.packages.multi_cloud import MultiCloudData, multi_cloud_package
from optimizer.packages.network import network_package


class BenchParams(TypedDict):
    cr_count: int
    cs_count: int
    cs_count_per_cr: int
    csp_count: int
    loc_count: int
    cr_to_loc_connections: int
    cr_to_cr_connections: int


DEFAULT_PARAMS: BenchParams = {
    "cr_count": 50,
    "cs_count": 250,
    "cs_count_per_cr": 50,
    "csp_count": 2,
    "loc_count": 10,
    "cr_to_loc_connections": 5,
    "cr_to_cr_connections": 1,
}


def bench() -> None:
    print("\n\n=== CSP_COUNT ===")
    bench_csp_count()

    print("\n\n=== LOC_COUNT ===")
    bench_loc_count()

    print("\n\n=== CR_TO_LOC_CONNECTIONS ===")
    bench_cr_to_loc_connections()

    print("\n\n=== CR_TO_CR_CONNECTIONS ===")
    bench_cr_to_cr_connections()

    print("\n\n=== CR_COUNT ===")
    bench_cr_count()

    print("\n\n=== CS_COUNT ===")
    bench_cs_count()

    print("\n\n=== CS_COUNT_PER_CR ===")
    bench_cs_count_per_cr()


def bench_cr_count() -> None:
    cr_counts = [10, 25, 50, 100, 200, 500]

    for cr_count in cr_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "cr_count": cr_count}  # type: ignore
        bench_instance(params)


def bench_cs_count() -> None:
    cs_counts = [10, 25, 50, 100, 200, 500]

    for cs_count in cs_counts:
        # misc: ignore
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cs_count": cs_count,
            "cs_count_per_cr": cs_count,
        }
        bench_instance(params)


def bench_cs_count_per_cr() -> None:
    cs_count_per_crs = [10, 25, 50, 100, 200]

    for cs_count_per_cr in cs_count_per_crs:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "cs_count_per_cr": cs_count_per_cr}  # type: ignore
        bench_instance(params)


def bench_csp_count() -> None:
    csp_counts = [1, 2, 3, 4]

    for csp_count in csp_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "csp_count": csp_count}  # type: ignore
        bench_instance(params)


def bench_loc_count() -> None:
    loc_counts = [10, 25, 50, 100, 200]

    for loc_count in loc_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "loc_count": loc_count}  # type: ignore
        bench_instance(params)


def bench_cr_to_loc_connections() -> None:
    cr_to_loc_connections_list = [0, 10, 25, 50, 100, 200]

    for cr_to_loc_connections in cr_to_loc_connections_list:
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cr_to_loc_connections": cr_to_loc_connections,
            "loc_count": max(DEFAULT_PARAMS["loc_count"], cr_to_loc_connections),
        }
        bench_instance(params)


def bench_cr_to_cr_connections() -> None:
    cr_to_cr_connections_list = [0, 1, 2, 3, 4, 5]

    for cr_to_cr_connections in cr_to_cr_connections_list:
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cr_to_cr_connections": cr_to_cr_connections,
        }
        bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)

    try:
        solution = optimizer.solve(PULP_CBC_CMD(msg=False))
        print_result(f"{params}", solution)
    except InfeasibleError:
        print(f"- {params}  INFEASIBLE")


def get_optimizer(params: BenchParams) -> InitializedOptimizer:
    cr_count = params["cr_count"]
    cs_count = params["cs_count"]
    cs_count_per_cr = params["cs_count_per_cr"]
    csp_count = params["csp_count"]
    loc_count = params["loc_count"]
    cr_to_loc_connections = params["cr_to_loc_connections"]
    cr_to_cr_connections = params["cr_to_cr_connections"]

    base_data = generate_base_data(cr_count, cs_count, cs_count_per_cr)

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

    return (
        Optimizer("bench_complete", sense=LpMinimize)
        .add_package(base_package)
        .add_package(network_package)
        .add_package(multi_cloud_package)
        .initialize(base_data, network_data, multi_data)
    )
