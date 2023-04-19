from datetime import timedelta
from typing import Any

from optiframe import StepData
from optiframe.framework import ModelSize, StepTimes

from optimizer.packages.base import BaseData
from optimizer.packages.base.data import CloudService, CloudResource
from optimizer.packages.network import NetworkData
from optimizer.packages.network.data import Location
from optimizer.solver import get_pulp_solver, Solver


def get_solver_from_args() -> Any:
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark the optimizer."
    )
    parser.add_argument(
        "--solver",
        choices=["cbc", "gurobi", "scip", "fscip"],
        default="cbc",
        help="The solver to use to solve the mixed-integer program.",
    )

    args = parser.parse_args()

    if args.solver == "cbc":
        solver = Solver.CBC
    elif args.solver == "gurobi":
        solver = Solver.GUROBI
    elif args.solver == "scip":
        solver = Solver.SCIP
    elif args.solver == "fscip":
        solver = Solver.FSCIP
    else:
        raise RuntimeError(f"Unsupported solver {args.solver}")

    return get_pulp_solver(solver=solver, msg=False)


def print_result(instance: str, solution: StepData) -> None:
    model_size: ModelSize = solution[ModelSize]
    step_times: StepTimes = solution[StepTimes]

    step_time_list = [
        (step_times.validate, "vd"),
        (step_times.pre_processing, "pp"),
        (step_times.build_mip, "bm"),
        (step_times.solve, "sv"),
        (step_times.extract_solution, "es"),
    ]

    total_time = sum((time for time, _ in step_time_list), timedelta())
    step_time_str = " -> ".join(f"{name} {format_time(time)}" for time, name in step_time_list)

    print(f"- {instance}")
    print(f"    model_size: {model_size.variable_count:,} x {model_size.constraint_count:,}")
    print(f"    time: {format_time(total_time)} ({step_time_str})")


def format_time(time: timedelta) -> str:
    return f"{time.total_seconds():.3f}s"


def generate_base_data(cr_count: int, cs_count: int, cs_count_per_cr: int) -> BaseData:
    assert cs_count_per_cr <= cs_count

    cloud_resources = [f"cr_{cr}" for cr in range(cr_count)]
    cloud_services = [f"cs_{cs}" for cs in range(cs_count)]

    cr_to_cs_list = dict()

    for cr_num, cr in enumerate(cloud_resources):
        cs_list: set[CloudService] = set()

        for i in range(cs_count_per_cr):
            idx = (i * 119428 + 3 * cr_num + 83) % cs_count
            j = 0

            while len(cs_list) < i + 1:
                cs_list.add(cloud_services[(idx + j) % cs_count])
                j += 1

        cr_to_cs_list[cr] = list(cs_list)

    base_data = BaseData(
        cloud_resources=cloud_resources,
        cloud_services=cloud_services,
        cs_to_base_cost={
            f"cs_{cs}": cs % 100 + (cs % 20) * (cs % 5) + 10 for cs in range(cs_count)
        },
        cr_to_cs_list=cr_to_cs_list,
        cr_to_instance_demand={f"cr_{cr}": (cr % 4) * 250 + 1 for cr in range(cr_count)},
    )

    assert (
        len(base_data.cloud_resources) == cr_count
    ), f"cr_count {len(base_data.cloud_resources)} != {cr_count}"
    assert (
        len(base_data.cloud_services) == cs_count
    ), f"cs_count {len(base_data.cloud_services)} != {cs_count}"

    for cr in base_data.cloud_resources:
        count = len(base_data.cr_to_cs_list[cr])
        assert count == cs_count_per_cr, f"cs_count_per_cr({cr}) {count} != {cs_count_per_cr}"

    return base_data


def generate_network_data(
    cr_count: int,
    cs_count: int,
    loc_count: int,
    cr_to_loc_connections: int,
    cr_to_cr_connections: int,
) -> NetworkData:
    locations = set(f"loc_{loc}" for loc in range(loc_count))
    cr_and_loc_to_traffic: dict[tuple[CloudResource, Location], int] = dict()
    cr_and_loc_to_max_latency: dict[tuple[CloudResource, Location], int] = dict()
    cr_and_cr_to_traffic: dict[tuple[CloudResource, Location], int] = dict()
    cr_and_cr_to_max_latency: dict[tuple[CloudResource, CloudResource], int] = dict()

    for i in range(cr_to_loc_connections):
        cr = (i * 1239 + i) % cr_count
        loc = (i * 912 + 32) % loc_count
        j = 0

        while len(cr_and_loc_to_traffic.keys()) < i + 1:
            cr = (cr + j) % cr_count
            loc = (loc + j + j % 2) % loc_count

            cr_and_loc_to_traffic[(f"cr_{cr}", f"loc_{loc}")] = abs(loc - cr)
            cr_and_loc_to_max_latency[(f"cr_{cr}", f"loc_{loc}")] = abs(cr - loc) % 40 + 5

            j += 1

    for i in range(cr_to_cr_connections):
        cr1 = (i * 2234 + i) % cr_count
        cr2 = (i * i + 5 * i + 992) % cr_count
        j = 0

        while len(cr_and_cr_to_traffic.keys()) < i + 1:
            cr1 = (cr1 + j) % cr_count
            cr2 = (cr2 + j + j % 2) % cr_count

            cr_and_cr_to_traffic[(f"cr_{cr1}", f"cr_{cr2}")] = (cr1 + cr2 + i) % 500
            cr_and_cr_to_max_latency[(f"cr_{cr1}", f"cr_{cr2}")] = abs(cr2 - cr1 + i) % 50 + 5

            j += 1

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

    assert len(locations) == loc_count, f"loc_count {len(locations)} != {loc_count}"
    assert (
        len(cr_and_loc_to_traffic.keys()) == cr_to_loc_connections
    ), f"cr_and_loc_to_traffic {len(cr_and_loc_to_traffic.keys())} != {cr_to_loc_connections}"
    assert (
        len(cr_and_cr_to_traffic.keys()) == cr_to_cr_connections
    ), f"cr_and_cr_to_traffic {len(cr_and_cr_to_traffic.keys())} != {cr_to_cr_connections}"

    return network_data
