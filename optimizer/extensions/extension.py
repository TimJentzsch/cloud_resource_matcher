from abc import ABC, abstractmethod

from optimizer.extensions.decorators import DependencyInfo


class Extension(ABC):
    @staticmethod
    @abstractmethod
    def identifier() -> str:
        pass

    @abstractmethod
    def validate(self) -> DependencyInfo:
        pass

    @abstractmethod
    def extend_mip(self) -> DependencyInfo:
        pass
