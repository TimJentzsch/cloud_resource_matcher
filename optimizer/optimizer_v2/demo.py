import dataclasses

from .extension import Extension
from .step import Step


@dataclasses.dataclass
class FirstData:
    foo: int


@dataclasses.dataclass
class SecondData:
    bar: int


class FirstExt(Extension[FirstData]):
    def __init__(self):
        pass

    def action(self) -> FirstData:
        print("First!")
        return FirstData(foo=1)


class SecondExt(Extension[SecondData]):
    first_data: FirstData

    def __init__(self, first_data: FirstData):
        self.first_data = first_data
        pass

    def action(self) -> SecondData:
        print(f"Second {self.first_data.foo}!")
        return SecondData(bar=2)


# TODO: Remove this
def main():
    step = Step().register_extension(FirstExt).register_extension(SecondExt)
