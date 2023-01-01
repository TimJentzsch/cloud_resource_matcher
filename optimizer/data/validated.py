from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")


@dataclass
class Validated(Generic[T]):
    """Data that is guaranteed to be valid.

    This should be constructed by using the `.validate` functions of the data types.
    When constructing this type directly, you _must_ ensure that the data is always valid.
    """
    data: T
