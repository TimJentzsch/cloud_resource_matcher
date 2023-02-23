from abc import ABC, abstractmethod

from .decorators import DependencyInfo


# A unique identifier for an extension
ExtensionId = str


class Extension(ABC):
    @staticmethod
    @abstractmethod
    def identifier() -> ExtensionId:
        pass

    @staticmethod
    @abstractmethod
    def validate() -> DependencyInfo:
        pass

    @staticmethod
    @abstractmethod
    def extend_mip() -> DependencyInfo:
        pass

    @staticmethod
    @abstractmethod
    def extract_solution() -> DependencyInfo:
        pass
