from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterator, List, TypeVar

from modupipe.base import Condition

Input = TypeVar("Input")
Output = TypeVar("Output")
NextOutput = TypeVar("NextOutput")


class Mapper(ABC, Generic[Input, Output]):
    @abstractmethod
    def map(self, items: Iterator[Input]) -> Iterator[Output]:
        pass

    def with_next(self, next: Mapper[Output, NextOutput]) -> Mapper[Input, NextOutput]:
        return Next(self, next)

    def __add__(self, next: Mapper[Output, NextOutput]) -> Mapper[Input, NextOutput]:
        return self.with_next(next)


class Next(Mapper[Input, NextOutput], Generic[Input, Output, NextOutput]):
    def __init__(
        self, mapper: Mapper[Input, Output], next: Mapper[Output, NextOutput]
    ) -> None:
        self.mapper = mapper
        self.next = next

    def map(self, input: Iterator[Input]) -> Iterator[NextOutput]:
        output = self.mapper.map(input)
        return self.next.map(output)


class Filter(Mapper[Input, Input], Generic[Input]):
    def __init__(self, condition: Condition[Input]) -> None:
        self.condition = condition

    def map(self, items: Iterator[Input]) -> Iterator[Input]:
        for item in items:
            if self.condition.check(item):
                yield item


class ToString(Mapper[Input, str], Generic[Input]):
    def map(self, items: Iterator[Input]) -> Iterator[str]:
        for item in items:
            yield str(item)


class Buffer(Mapper[Input, List[Input]], Generic[Input]):
    def __init__(self, size: int) -> None:
        self.size = size
        self.buffer: List[Input] = []

    def map(self, items: Iterator[Input]) -> Iterator[List[Input]]:
        for item in items:
            self.buffer.append(item)

            if len(self.buffer) >= self.size:
                yield self.buffer
                self.buffer = []
