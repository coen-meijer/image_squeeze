from event import Event


class ColumnEvent(Event):

    def __lt__(self, other):
        self.time < other.time
