import abc
from typing import TypeVar, Generic

T = TypeVar("T")


class Extension(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def action(self) -> T:
        pass
