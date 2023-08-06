from __future__ import annotations

from abc import ABC, abstractmethod
from random import random
from typing import Generic, Iterator, TypeVar

from modupipe.exceptions import MaxIterationsReached
from modupipe.mapper import Mapper
from modupipe.queue import Queue, QueueGetStrategy

Data = TypeVar("Data")
MappedData = TypeVar("MappedData")


class Source(ABC, Generic[Data]):
    @abstractmethod
    def fetch(self) -> Iterator[Data]:
        pass

    def mapped_with(self, mapper: Mapper[Data, MappedData]) -> Source[MappedData]:
        return MappedSource(self, mapper)

    def __add__(self, mapper: Mapper[Data, MappedData]) -> Source[MappedData]:
        return self.mapped_with(mapper)


class MappedSource(Source[MappedData], Generic[Data, MappedData]):
    def __init__(self, source: Source[Data], mapper: Mapper[Data, MappedData]) -> None:
        self.source = source
        self.mapper = mapper

    def fetch(self) -> Iterator[MappedData]:
        return self.mapper.map(self.source.fetch())


class QueueSource(Source[Data]):
    def __init__(self, queue: Queue[Data], strategy: QueueGetStrategy[Data]) -> None:
        self.queue = queue
        self.strategy = strategy

    def fetch(self) -> Iterator[Data]:
        while True:
            yield self.strategy.get(self.queue)


class RandomSource(Source[float]):
    def fetch(self) -> Iterator[float]:
        while True:
            yield random()


class MaxIterations(Source[Data]):
    def __init__(self, source: Source[Data], nb_iterations: int) -> None:
        self.source = source
        self.nb_iterations = nb_iterations

    def fetch(self) -> Iterator[Data]:
        for i, item in enumerate(self.source.fetch()):
            if i >= self.nb_iterations:
                raise MaxIterationsReached()

            yield item
