import traceback
from abc import ABC, abstractmethod
from multiprocessing import Process
from threading import Thread
from typing import Generic, List, TypeVar

from modupipe.sink import Sink
from modupipe.source import Source

Data = TypeVar("Data")


class Runnable(ABC):
    @abstractmethod
    def run(self):
        pass


class Pipeline(Runnable, Generic[Data]):
    def __init__(self, source: Source[Data], sink: Sink[Data]) -> None:
        self.source = source
        self.sink = sink

    def run(self):
        for item in self.source.fetch():
            self.sink.receive(item)


class Retry(Runnable):
    def __init__(self, runnable: Runnable, nb_times: int) -> None:
        self.runnable = runnable
        self.max_retries = nb_times

    def run(self):
        retries = 0

        while True:
            try:
                self.runnable.run()
            except Exception as e:
                if retries >= self.max_retries:
                    raise e
                else:
                    print("An exception occured while running pipeline :")
                    print(traceback.format_exc())
                    retries += 1


class MultiThread(Runnable):
    def __init__(self, runnables: List[Runnable]) -> None:
        self.threads = [
            Thread(name=runnable.__class__.__name__, target=runnable.run)
            for runnable in runnables
        ]

    def run(self) -> None:
        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()


class MultiProcess(Runnable):
    def __init__(self, runnables: List[Runnable]) -> None:
        self.processes = [
            Process(name=runnable.__class__.__name__, target=runnable.run)
            for runnable in runnables
        ]

    def run(self) -> None:
        for process in self.processes:
            process.start()

        for process in self.processes:
            process.join()
