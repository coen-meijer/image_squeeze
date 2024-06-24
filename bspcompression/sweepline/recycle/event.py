from abc import ABC, abstractmethod, abstractproperty


class Event(ABC):

    @abstractmethod
    def __lt__(self, other):
        pass

