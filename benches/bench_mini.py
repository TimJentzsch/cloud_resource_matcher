from typing import TypedDict

from optiframe import Optimizer, InfeasibleError
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result
from optimizer.packages.base import BaseData, base_package


class BenchParams(TypedDict):
    cr_count: int
    cs_count: int
    cs_count_per_cr: int


def bench() -> None:
    params: BenchParams = {
        'cr_count': 1,
        'cs_count': 1,
        'cs_count_per_cr': 1
    }
    bench_instance(params)


def bench_instance(params: BenchParams) -> None:
    optimizer = get_optimizer(params)

    try:
        solution = optimizer.print_mip_and_solve(PULP_CBC_CMD(msg=False))
        print_result(f"{params}", solution)
    except InfeasibleError:
        print(f"- {params}  INFEASIBLE")


def get_optimizer(params: BenchParams) -> InitializedOptimizer:
    cr_count = params["cr_count"]
    cs_count = params["cs_count"]
    cs_count_per_cr = params["cs_count_per_cr"]

    base_data = BaseData(
        cloud_resources=[f"cr_{cr}" for cr in range(cr_count)],
        cloud_services=[f"cs_{cs}" for cs in range(cs_count)],
        cs_to_base_cost={
            f"cs_{cs}": cs % 100 + (cs % 20) * (cs % 5) + 10 for cs in range(cs_count)
        },
        cr_to_cs_list={
            f"cr_{cr}": list(
                set(
                    f"cs_{cs}"
                    for cs in range(cs_count)
                    if ((cr + cs) % (cs_count / cs_count_per_cr)) == 0
                )
            )
            for cr in range(cr_count)
        },
        cr_to_instance_demand={f"cr_{cr}": (cr % 4) * 250 + 1 for cr in range(cr_count)},
    )

    return Optimizer("bench_base", sense=LpMinimize).add_package(base_package).initialize(base_data)
