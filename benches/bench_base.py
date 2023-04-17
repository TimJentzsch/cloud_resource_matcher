from optiframe import Optimizer
from optiframe.framework import InitializedOptimizer
from pulp import LpMinimize, PULP_CBC_CMD

from benches.utils import print_result
from optimizer.packages.base import BaseData, base_package


def bench() -> None:
    benches = [
        (10, 10, 2),
        (20, 20, 4),
        (30, 30, 6),
        (50, 50, 10),
        (100, 100, 20),
        (500, 500, 50),
        (500, 500, 500),
        (1000, 1000, 50),
    ]

    for cr_count, cs_count, cs_count_per_cr in benches:
        optimizer = get_optimizer(cr_count, cs_count, cs_count_per_cr)
        solution = optimizer.solve(PULP_CBC_CMD(msg=False))
        print_result(
            f"cr_count: {cr_count}, cs_count: {cs_count}, cs_count_per_cr: {cs_count_per_cr}",
            solution,
        )


def get_optimizer(cr_count: int, cs_count: int, cs_count_per_cr: int) -> InitializedOptimizer:
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

    return (
        Optimizer(f"bench_base", sense=LpMinimize).add_package(base_package).initialize(base_data)
    )
