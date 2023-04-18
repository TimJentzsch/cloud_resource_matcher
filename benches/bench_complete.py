from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result
from optimizer.packages.base import BaseData, base_package
from optimizer.packages.multi_cloud import MultiCloudData, multi_cloud_package
from optimizer.packages.network import NetworkData, network_package
from optimizer.packages.performance import PerformanceData, performance_package


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
    "cs_count_per_cr": 100,
    "csp_count": 3,
    "loc_count": 50,
    "cr_to_loc_connections": 25,
    "cr_to_cr_connections": 25,
}


def bench() -> None:
    print("=== CR_COUNT ===")
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
    cr_counts = [10, 25, 50, 100, 200, 500]

    for cr_count in cr_counts:
        params: BenchParams = {**DEFAULT_PARAMS, "cr_count": cr_count}
        bench_instance(params)


def bench_cs_count() -> None:
    cs_counts = [10, 25, 50, 100, 200, 500]

    for cs_count in cs_counts:
        params: BenchParams = {**DEFAULT_PARAMS, "cs_count": cs_count, "cs_count_per_cr": cs_count}
        bench_instance(params)


def bench_cs_count_per_cr() -> None:
    cs_count_per_crs = [10, 25, 50, 100, 200, 500]

    for cs_count_per_cr in cs_count_per_crs:
        params: BenchParams = {**DEFAULT_PARAMS, "cs_count_per_cr": cs_count_per_cr}
        bench_instance(params)


def bench_csp_count() -> None:
    csp_counts = [1, 2, 3, 4]

    for csp_count in csp_counts:
        params: BenchParams = {**DEFAULT_PARAMS, "csp_count": csp_count}
        bench_instance(params)


def bench_loc_count() -> None:
    loc_counts = [10, 25, 50, 100, 200]

    for loc_count in loc_counts:
        params: BenchParams = {**DEFAULT_PARAMS, "loc_count": loc_count}
        bench_instance(params)


def bench_cr_to_loc_connections() -> None:
    cr_to_loc_connections_list = [0, 10, 25, 50, 100, 200]

    for cr_to_loc_connections in cr_to_loc_connections_list:
        params: BenchParams = {**DEFAULT_PARAMS, "cr_to_loc_connections": cr_to_loc_connections}
        bench_instance(params)


def bench_cr_to_cr_connections() -> None:
    cr_to_cr_connections_list = [0, 10, 25, 50, 100, 200]

    for cr_to_cr_connections in cr_to_cr_connections_list:
        params: BenchParams = {**DEFAULT_PARAMS, "cr_to_cr_connections": cr_to_cr_connections}
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

    base_data = BaseData(
        cloud_resources=[f"cr_{cr}" for cr in range(cr_count)],
        cloud_services=[f"cs_{cs}" for cs in range(cs_count)],
        cs_to_base_cost={
            f"cs_{cs}": cs % 100 + (cs % 20) * (cs % 5) + 10 for cs in range(cs_count)
        },
        cr_to_cs_list={
            f"cr_{cr}": [
                f"cs_{cs}"
                for cs in range(cs_count)
                if ((cr + cs) % (cs_count / cs_count_per_cr)) == 0
            ]
            for cr in range(cr_count)
        },
        cr_to_instance_demand={f"cr_{cr}": (cr % 4) * 250 + 1 for cr in range(cr_count)},
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

    locations = set(f"loc_{loc}" for loc in range(loc_count))
    cr_and_loc_to_traffic = dict()
    cr_and_loc_to_max_latency = dict()
    cr_and_cr_to_traffic = dict()
    cr_and_cr_to_max_latency = dict()

    for i in range(cr_to_loc_connections):
        cr = (i * 1239 + i) % cr_count
        loc = (i * 912 + 32) % loc_count

        cr_and_loc_to_traffic[(f"cr_{cr}", f"loc_{loc}")] = abs(loc - cr)
        cr_and_loc_to_max_latency[(f"cr_{cr}", f"loc_{loc}")] = abs(cr - loc) % 40 + 5

    for i in range(cr_to_cr_connections):
        cr1 = (i * 2234 + i) % cr_count
        cr2 = (i * i + 5 * i + 992) % cr_count

        cr_and_cr_to_traffic[(f"cr_{cr1}", f"cr_{cr2}")] = (cr1 + cr2 + i) % 500
        cr_and_cr_to_max_latency[(f"cr_{cr1}", f"cr_{cr2}")] = abs(cr2 - cr1 + i) % 50 + 5

    network_data = NetworkData(
        locations=locations,
        cs_to_loc={f"cs_{cs}": f"loc_{cs % loc_count}" for cs in range(cs_count)},
        loc_and_loc_to_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) % 40
            for loc1 in range(loc_count)
            for loc2 in range(loc_count)
        },
        loc_and_loc_to_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0 if loc1 == loc2 else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(loc_count)
            for loc2 in range(loc_count)
        },
        cr_and_loc_to_traffic=cr_and_loc_to_traffic,
        cr_and_loc_to_max_latency=cr_and_loc_to_max_latency,
        cr_and_cr_to_max_latency=cr_and_cr_to_max_latency,
        cr_and_cr_to_traffic=cr_and_cr_to_traffic,
    )

    return (
        Optimizer(f"bench_complete", sense=LpMinimize)
        .add_package(base_package)
        .add_package(network_package)
        .add_package(multi_cloud_package)
        .initialize(base_data, network_data, multi_data)
    )
