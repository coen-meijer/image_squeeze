import fractions

from sweepline.recycle.linecrossevent import LineCrossEvent


class CrossLine:

    def __init__(self, slope, intercept, sweepline_index):
        self.slope = slope
        self.intercept = intercept
        self.index = sweepline_index

    def crossing(self, other_line):
        if self.slope == other_line.slope:
            return None
        # otherwise ...
        if bool(self.sweepline_index < other_line.sweepline_index) ^ bool(self.slope < other_line.slope):
            crossing = fractions.Fraction(self.intercept - other_line.intercept, self.slope - other_line.slope)
            return LineCrossEvent(crossing, self, other_line)
        return None


