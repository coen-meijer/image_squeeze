from abc import ABC, abstractmethod


class SweepLine(ABC):

    @abstractmethod
    def trigger(self):
        pass

