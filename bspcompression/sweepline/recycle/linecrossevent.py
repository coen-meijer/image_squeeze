from sweepline.recycle.event import Event


class LineCrossEvent(Event):

    def __init__(self, time, line, crossing_line):
        self.time = time
        self.line = line
        self.crossing_line = crossing_line
        self.continuing = True

    def __lt__(self, other):
        return self.time < other.time


