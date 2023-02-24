import inspect
from typing import Self, Type

from .extension import Extension


class Step:
    extensions: list[Type[Extension]]

    def __init__(self):
        self.extensions = []

    def register_extension(self, extension: Type[Extension]) -> Self:
        self.extensions.append(extension)

        print(inspect.signature(extension.action))
        print("Signature", inspect.signature(extension))
        return self
