from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

from optimizer.data.types import Cost
from optimizer.data import BaseData, PerformanceData, NetworkData, MultiCloudData
from optimizer.framework import Optimizer
from optimizer.framework.tasks import SolutionCost
from optimizer.packages import BASE_PACKAGE, PERFORMANCE_PACKAGE, NETWORK_PACKAGE, MULTI_CLOUD_PACKAGE
from optimizer.packages.base import BaseSolution
from optimizer.solving import SolveError
from optimizer.solver import Solver


@dataclass
class SolveSolution:
    cost: Cost
    base: BaseSolution


def solve_demo_model(
    vm_count: int,
    service_count: int,
    time_count: int,
    csp_count: int,
    location_count: int,
    solver: Solver = Solver.CBC,
    time_limit: Optional[timedelta] = None,
    cost_gap_abs: Optional[Cost] = None,
    cost_gap_rel: Optional[float] = None,
) -> SolveSolution:
    """Create and solve a model based on demo data."""
    base_data = BaseData(
        virtual_machines=[f"vm_{v}" for v in range(vm_count)],
        services=[f"service_{s}" for s in range(service_count)],
        service_base_costs={
            f"service_{s}": s % 100 + (s % 20) * (s % 5) + 10 for s in range(service_count)
        },
        virtual_machine_services={
            f"vm_{v}": [f"service_{s}" for s in range(service_count) if ((v + s) % 4) == 0]
            for v in range(vm_count)
        },
        time=list(range(time_count)),
        virtual_machine_demand={
            (f"vm_{v}", t): (v % 2) * (t % 3) + 1
            for v in range(vm_count)
            for t in range(time_count)
        },
        max_service_instances={},
    )

    perf_data = PerformanceData(
        virtual_machine_min_ram={f"vm_{v}": v % 4 + 1 for v in range(vm_count)},
        virtual_machine_min_cpu_count={f"vm_{v}": (v + 2) % 3 + 1 for v in range(vm_count)},
        service_ram={f"service_{s}": (s + 4) % 30 + 5 for s in range(service_count)},
        service_cpu_count={f"service_{s}": s % 23 + 1 for s in range(service_count)},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=[f"csp_{k}" for k in range(csp_count)],
        cloud_service_provider_services={
            f"csp_{k}": [f"service_{s}" for s in range(service_count) if s % csp_count == k]
            for k in range(csp_count)
        },
        min_cloud_service_provider_count=2,
        max_cloud_service_provider_count=3,
    )

    network_data = NetworkData(
        locations=set(f"loc_{loc}" for loc in range(location_count)),
        service_location={
            f"service_{s}": f"loc_{s % location_count}" for s in range(service_count)
        },
        location_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) * 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        location_traffic_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0 if loc1 == loc2 else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        virtual_machine_location_traffic={
            (f"vm_{v}", f"loc_{loc}"): abs(loc - v) if loc % 4 == v % 2 else 0
            for v in range(vm_count)
            for loc in range(location_count)
        },
        virtual_machine_location_max_latency={
            (f"vm_{v}", f"loc_{loc}"): v % 20 + 20
            for v in range(vm_count)
            for loc in range(location_count)
        },
        virtual_machine_virtual_machine_max_latency={},
        virtual_machine_virtual_machine_traffic={},
    )

    data = (
        Optimizer().add_package(BASE_PACKAGE).add_package(PERFORMANCE_PACKAGE).add_package(NETWORK_PACKAGE).add_package(MULTI_CLOUD_PACKAGE)
        .initialize(base_data, perf_data, network_data, multi_data)
        .validate()
        .build_mip()
        .solve(
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=cost_gap_abs,
            cost_gap_rel=cost_gap_rel,
        )
    )

    return SolveSolution(cost=data[SolutionCost].cost, base=data[BaseSolution])


def main():
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
        "--vm-count",
        type=int,
        default=50,
        help="The number of virtual machines (VMs) in the demo data.",
    )
    parser.add_argument(
        "--service-count",
        type=int,
        default=50,
        help="The number of cloud services in the demo data.",
    )
    parser.add_argument(
        "--time-count",
        type=int,
        default=400,
        help="The number of discrete time units in the demo data.",
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
            vm_count=args.vm_count,
            service_count=args.service_count,
            time_count=args.time_count,
            location_count=args.location_count,
            csp_count=args.csp_count,
            solver=solver,
            time_limit=time_limit,
            cost_gap_abs=args.cost_gap_abs,
            cost_gap_rel=args.cost_gap_rel,
        )

        duration = datetime.now() - start_time

        print("=== SOLUTION FOUND ===\n")
        print(f"Cost: {solution.cost}")
        print(f"Duration: {duration.total_seconds():.2f}s")
    except SolveError as e:
        duration = datetime.now() - start_time

        print("=== PROBLEM INFEASIBLE ===\n")
        print(f"{e.reason}")
        print(f"Duration: {duration.total_seconds():.2f}s")
        exit(101)
