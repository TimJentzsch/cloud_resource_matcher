from datetime import timedelta

from optiframe import StepData
from optiframe.framework import ModelSize, StepTimes

from optimizer.packages.base import BaseData


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
        cs_list = set()

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

    assert len(base_data.cloud_resources) == cr_count, f"cr_count {len(base_data.cloud_resources)} != {cr_count}"
    assert len(base_data.cloud_services) == cs_count, f"cs_count {len(base_data.cloud_services)} != {cs_count}"

    for cr in base_data.cloud_resources:
        count = len(base_data.cr_to_cs_list[cr])
        assert count == cs_count_per_cr, f"cs_count_per_cr({cr}) {count} != {cs_count_per_cr}"

    return base_data
