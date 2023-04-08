from optiframe.framework.tasks import BuildMipTask


class BuildMipPerformanceTask(BuildMipTask[None]):
    def __init__(self) -> None:
        pass

    def execute(self) -> None:
        """The constraints are enforced entirely in the pre-processing step."""
        pass
