from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Condition(ABC, Generic[T]):
    @abstractmethod
    def check(self, item: T) -> bool:
        pass
