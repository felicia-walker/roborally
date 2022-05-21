from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class ValueObject(ABC, Generic[T]):

    def __init__(self):
        pass

    def __eq__(self, other: T) -> bool:
        if other is None:
            return False

        return self.equals_core(other)

    @abstractmethod
    def equals_core(self, value_object: T) -> bool:
        pass
