from sweepline.recycle.event import Event


class FunctionEvent(Event, ABC):

    def __init__(self, time, function):
        self.time = time
        self.function = function

    def __lt__(self, other):
        return self.time < other.time

    def trigger(self):
        self.function()
