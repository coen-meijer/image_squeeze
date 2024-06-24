from abc import ABC, abstractmethod


class EventTask(ABC):

    @abstractmethod
    def execute(self):
        pass
