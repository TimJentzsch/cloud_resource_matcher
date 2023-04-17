from optiframe import Optimizer, StepData
from optiframe.framework import InitializedOptimizer, ModelSize, StepTimes
from pulp import LpMinimize, COIN, COIN_CMD, PULP_CBC_CMD

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


def print_result(instance: str, solution: StepData) -> None:
    model_size: ModelSize = solution[ModelSize]
    step_times: StepTimes = solution[StepTimes]

    validate_time = f"{step_times.validate.total_seconds():.3f}s"
    pre_processing_time = f"{step_times.pre_processing.total_seconds():.3f}s"
    build_mip_time = f"{step_times.build_mip.total_seconds():.3f}s"
    solve_time = f"{step_times.solve.total_seconds():.3f}s"
    extract_solution_time = f"{step_times.extract_solution.total_seconds():.3f}s"

    total_timedelta = (
        step_times.validate
        + step_times.pre_processing
        + step_times.build_mip
        + step_times.solve
        + step_times.extract_solution
    )
    total_time = f"{total_timedelta.total_seconds():.3f}s"

    print(f"- {instance}")
    print(f"    model_size: {model_size.variable_count:,} x {model_size.constraint_count:,}")
    print(f"    time: {total_time}")
    print(f"        - {validate_time} (validate)")
    print(f"        - {pre_processing_time} (pre_processing)")
    print(f"        - {build_mip_time} (build_mip)")
    print(f"        - {solve_time} (solve)")
    print(f"        - {extract_solution_time} (extract_solution)")


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
        Optimizer(f"bench_{cr_count},{cs_count},{cs_count_per_cr}", sense=LpMinimize)
        .add_package(base_package)
        .initialize(base_data)
    )
