from datetime import timedelta

from optiframe.framework import StepTimes, ModelSize


def get_total_time(step_times: StepTimes) -> timedelta:
    """Calculate the total time needed in all steps together."""
    return sum(
        [
            step_times.validate,
            step_times.pre_processing,
            step_times.build_mip,
            step_times.solve,
            step_times.extract_solution,
        ],
        timedelta(),
    )


def get_model_size(model_size: ModelSize) -> int:
    """Calculate the total size of the model (variable count * constraint count)."""
    return model_size.variable_count * model_size.constraint_count
