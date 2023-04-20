from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize

from benches.utils import (
    print_result,
    generate_base_data,
    generate_network_data,
    get_solver_from_args,
)
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
    "cr_count": 500,
    "cs_count": 500,
    "cs_count_per_cr": 200,
    "csp_count": 3,
    "loc_count": 500,
    "cr_to_loc_connections": 40,
    "cr_to_cr_connections": 10,
}


def bench() -> None:
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

    print("\n\n=== CR_TO_CR_CONNECTIONS ===")
    bench_cr_to_cr_connections()


def bench_cr_count() -> None:
    cr_counts = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    for cr_count in cr_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "cr_count": cr_count}  # type: ignore
        bench_instance(params)


def bench_cs_count() -> None:
    cs_counts = [200, 300, 400, 500, 600, 700, 800, 900, 1000]

    for cs_count in cs_counts:
        # misc: ignore
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cs_count": cs_count,
        }
        bench_instance(params)


def bench_cs_count_per_cr() -> None:
    cs_count_per_crs = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

    for cs_count_per_cr in cs_count_per_crs:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "cs_count_per_cr": cs_count_per_cr}  # type: ignore
        bench_instance(params)


def bench_csp_count() -> None:
    csp_counts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for csp_count in csp_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "csp_count": csp_count}  # type: ignore
        bench_instance(params)


def bench_loc_count() -> None:
    loc_counts = [100, 200, 300, 400, 500, 600, 700, 800, 1000]

    for loc_count in loc_counts:
        # misc: ignore
        params: BenchParams = {**DEFAULT_PARAMS, "loc_count": loc_count}  # type: ignore
        bench_instance(params)


def bench_cr_to_loc_connections() -> None:
    cr_to_loc_connections_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    for cr_to_loc_connections in cr_to_loc_connections_list:
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cr_to_loc_connections": cr_to_loc_connections,
            "loc_count": max(DEFAULT_PARAMS["loc_count"], cr_to_loc_connections),
        }
        bench_instance(params)


def bench_cr_to_cr_connections() -> None:
    cr_to_cr_connections_list = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40]

    for cr_to_cr_connections in cr_to_cr_connections_list:
        params: BenchParams = {
            **DEFAULT_PARAMS,  # type: ignore
            "cr_to_cr_connections": cr_to_cr_connections,
        }
        bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)
    solver = get_solver_from_args()

    try:
        solution = optimizer.solve(solver=solver)
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
