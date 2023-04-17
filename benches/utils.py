from optiframe import StepData
from optiframe.framework import ModelSize, StepTimes


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
