from sweepline.recycle.eventtask import EventTask


class PixelDualCrossTask(EventTask):

    def __init__(self, min_index, max_index, sweepline, point):
        self.min_index = min_index
        self.max_index = max_index
        self.sweepline = sweepline
        self.point = point

    def absorb(self, other):
        if self.point == other.point:
            self.min_index = min(self.min_index, other.min_index)
            self.max_index = max(self.min_index, other.max_index)
            return True
        return False

    def execute(self):
        self.sweepline[self.min_index:self.max_index] = reversed(self.sweepline[self.min_index:self.max_index])

