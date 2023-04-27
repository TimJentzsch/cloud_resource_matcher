from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

from pulp import LpMinimize

from optimizer.packages.base.data import Cost
from optiframe import Optimizer, SolutionObjValue, InfeasibleError
from optimizer.packages.base import BaseSolution, BaseData, base_package
from optimizer.packages.multi_cloud import MultiCloudData, multi_cloud_package
from optimizer.packages.network import NetworkData, network_package
from optimizer.packages.performance import PerformanceData, performance_package
from optimizer.solver import Solver, get_pulp_solver


@dataclass
class SolveSolution:
    cost: Cost
    base: BaseSolution


def solve_demo_model(
    cr_count: int,
    cs_count: int,
    csp_count: int,
    location_count: int,
    solver: Solver = Solver.CBC,
    time_limit: Optional[timedelta] = None,
    cost_gap_abs: Optional[Cost] = None,
    cost_gap_rel: Optional[float] = None,
) -> SolveSolution:
    """Create and solve a model based on demo data."""
    base_data = BaseData(
        cloud_resources=[f"cr_{cr}" for cr in range(cr_count)],
        cloud_services=[f"cs_{cs}" for cs in range(cs_count)],
        cs_to_base_cost={
            f"cs_{cs}": cs % 100 + (cs % 20) * (cs % 5) + 10 for cs in range(cs_count)
        },
        cr_to_cs_list={
            f"cr_{cr}": [f"cs_{cs}" for cs in range(cs_count) if ((cr + cs) % 4) == 0]
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
        cost_per_unit={(f"cs_{cs}", "RAM"): cs % 5 for cs in range(cs_count)},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=[f"csp_{csp}" for csp in range(csp_count)],
        csp_to_cs_list={
            f"csp_{csp}": [f"cs_{cs}" for cs in range(cs_count) if cs % csp_count == csp]
            for csp in range(csp_count)
        },
        min_csp_count=2,
        max_csp_count=3,
        csp_to_cost={f"csp_{csp}": csp * 10_000 for csp in range(csp_count)},
    )

    network_data = NetworkData(
        locations=set(f"loc_{loc}" for loc in range(location_count)),
        cs_to_loc={f"cs_{cs}": f"loc_{cs % location_count}" for cs in range(cs_count)},
        loc_and_loc_to_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) * 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        loc_and_loc_to_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0 if loc1 == loc2 else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        cr_and_loc_to_traffic={
            (f"cr_{cr}", f"loc_{loc}"): abs(loc - cr) if loc % 4 == cr % 2 else 0
            for cr in range(cr_count)
            for loc in range(location_count)
        },
        cr_and_loc_to_max_latency={
            (f"cr_{cr}", f"loc_{loc}"): cr % 20 + 20
            for cr in range(cr_count)
            for loc in range(location_count)
        },
        cr_and_cr_to_max_latency={},
        cr_and_cr_to_traffic={},
    )

    data = (
        Optimizer("cloud_cost_optimization", sense=LpMinimize)
        .add_modules(base_package, performance_package, network_package, multi_cloud_package)
        .initialize(base_data, perf_data, network_data, multi_data)
        .validate()
        .pre_processing()
        .build_mip()
        .solve(
            get_pulp_solver(
                solver=solver,
                time_limit=time_limit,
                cost_gap_abs=cost_gap_abs,
                cost_gap_rel=cost_gap_rel,
            )
        )
    )

    return SolveSolution(cost=data[SolutionObjValue].objective_value, base=data[BaseSolution])


def main() -> None:
    import logging
    import argparse

    logging.basicConfig(
        encoding="utf-8", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        description="Optimize the costs for cloud computing applications."
    )
    parser.add_argument(
        "--solver",
        choices=["cbc", "gurobi", "scip", "fscip"],
        default="cbc",
        help="The solver to use to solve the mixed-integer program.",
    )
    parser.add_argument(
        "--cr-count",
        type=int,
        default=500,
        help="The number of virtual machines (VMs) in the demo data.",
    )
    parser.add_argument(
        "--cs-count",
        type=int,
        default=500,
        help="The number of cloud cloud_cloud_services in the demo data.",
    )
    parser.add_argument(
        "--location-count",
        type=int,
        default=5,
        help="The number of locations in the demo data." "This is used for the networking data.",
    )
    parser.add_argument(
        "--csp-count",
        type=int,
        default=3,
        help="The number of cloud service providers (CSPs) in the demo data.",
    )
    parser.add_argument(
        "--time-limit-sec",
        type=float,
        default=None,
        help="The maximum amount of time to solve the problem, in seconds.",
    )
    parser.add_argument(
        "--cost-gap-abs",
        type=float,
        default=None,
        help="The absolute tolerance for the cost until the optimization stops.",
    )
    parser.add_argument(
        "--cost-gap-rel",
        type=float,
        default=None,
        help=(
            "The relative tolerance for the cost until the optimization stops. "
            "A fractional value between 0.0 and 1.0"
        ),
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

    if args.cost_gap_rel is not None:
        if args.cost_gap_rel < 0.0 or args.cost_gap_rel > 1.0:
            print(
                "--cost-gap-rel must be a value between 0.0 and 1.0, "
                f"but it's {args.cost_gap_rel}"
            )
            exit(102)
            return

    if args.time_limit_sec is not None:
        time_limit = timedelta(seconds=args.time_limit_sec)
    else:
        time_limit = None

    start_time = datetime.now()

    try:
        solution = solve_demo_model(
            cr_count=args.cr_count,
            cs_count=args.cs_count,
            location_count=args.location_count,
            csp_count=args.csp_count,
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=args.cost_gap_abs,
            cost_gap_rel=args.cost_gap_rel,
        )

        duration = datetime.now() - start_time

        print("\n=== SOLUTION FOUND ===\n")
        print(f"Cost: {solution.cost:,} €")
        print(f"Duration: {duration.total_seconds():.2f}s")
    except InfeasibleError:
        duration = datetime.now() - start_time

        print("\n=== PROBLEM INFEASIBLE ===\n")
        print(f"Duration: {duration.total_seconds():.2f}s")
        exit(101)
