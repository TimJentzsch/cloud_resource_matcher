from abc import ABC, abstractmethod

from optimizer.extensions.decorators import DependencyInfo


# A unique identifier for an extension
ExtensionId = str


class Extension(ABC):
    @staticmethod
    @abstractmethod
    def identifier() -> ExtensionId:
        pass

    @abstractmethod
    def validate(self) -> DependencyInfo:
        pass

    @abstractmethod
    def extend_mip(self) -> DependencyInfo:
        pass

    @abstractmethod
    def extract_solution(self) -> DependencyInfo:
        pass
