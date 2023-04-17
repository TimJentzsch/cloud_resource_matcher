from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result
from optimizer.packages.base import BaseData, base_package
from optimizer.packages.multi_cloud import MultiCloudData, multi_cloud_package
from optimizer.packages.network import NetworkData, network_package
from optimizer.packages.performance import PerformanceData, performance_package


def bench() -> None:
    benches = [
        (10, 10, 2, 1, 1, 0, 0),
        (20, 20, 4, 3, 2, 1, 1),
        (30, 30, 6, 3, 5, 2, 2),
        (50, 50, 10, 3, 10, 10, 3),
        (100, 100, 20, 3, 20, 10, 5),
        (500, 500, 50, 3, 50, 100, 30),
        (500, 500, 100, 3, 50, 100, 30),
        (1000, 1000, 50, 3, 50, 100, 30),
    ]

    for params in benches:
        optimizer = get_optimizer(*params)

        try:
            solution = optimizer.solve(PULP_CBC_CMD(msg=False))
        except InfeasibleError:
            print(f"- Infeasible {params}")
            continue

        print_result(
            f"{params}",
            solution,
        )


def get_optimizer(
    cr_count: int,
    cs_count: int,
    cs_count_per_cr: int,
    csp_count: int,
    location_count: int,
    cr_to_loc_connections: int,
    cr_to_cr_connections: int,
) -> InitializedOptimizer:
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

    perf_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM"],
        performance_demand={
            **{(f"cr_{cr}", "vCPUs"): (cr + 2) % 3 + 1 for cr in range(cr_count)},
            **{(f"cr_{cr}", "RAM"): cr % 4 + 1 for cr in range(cr_count)},
        },
        performance_supply={
            **{(f"cs_{cs}", "vCPUs"): (cs + 4) % 30 + 5 for cs in range(cs_count)},
            **{(f"cs_{cs}", "RAM"): cs % 23 + 1 for cs in range(cs_count)},
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

    locations = set(f"loc_{loc}" for loc in range(location_count))
    cr_and_loc_to_traffic = dict()
    cr_and_loc_to_max_latency = dict()
    cr_and_cr_to_traffic = dict()
    cr_and_cr_to_max_latency = dict()

    for i in range(cr_to_loc_connections):
        cr = (i * 1239 + i) % cr_count
        loc = (i * 912 + 32) % location_count

        cr_and_loc_to_traffic[(f"cr_{cr}", f"loc_{loc}")] = abs(loc - cr)
        cr_and_loc_to_max_latency[(f"cr_{cr}", f"loc_{loc}")] = abs(cr - loc) % 40 + 5

    for i in range(cr_to_cr_connections):
        cr1 = (i * 2234 + i) % cr_count
        cr2 = (i * i + 5 * i + 992) % cr_count

        cr_and_cr_to_traffic[(f"cr_{cr1}", f"cr_{cr2}")] = (cr1 + cr2 + i) % 500
        cr_and_cr_to_max_latency[(f"cr_{cr1}", f"cr_{cr2}")] = abs(cr2 - cr1 + i) % 50 + 5

    network_data = NetworkData(
        locations=locations,
        cs_to_loc={f"cs_{cs}": f"loc_{cs % location_count}" for cs in range(cs_count)},
        loc_and_loc_to_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) % 40
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        loc_and_loc_to_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0 if loc1 == loc2 else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        cr_and_loc_to_traffic=cr_and_loc_to_traffic,
        cr_and_loc_to_max_latency=cr_and_loc_to_max_latency,
        cr_and_cr_to_max_latency=cr_and_cr_to_max_latency,
        cr_and_cr_to_traffic=cr_and_cr_to_traffic,
    )

    return (
        Optimizer(f"bench_complete", sense=LpMinimize)
        .add_package(base_package)
        .add_package(performance_package)
        .add_package(network_package)
        .add_package(multi_cloud_package)
        .initialize(base_data, perf_data, network_data, multi_data)
    )
