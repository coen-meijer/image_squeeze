import fractions
import heapq


def crossing(line, other_line):
    if line.slope == other_line.slope:
        return None
    if bool(line.sweepline_index < other_line.sweepline_index) ^ bool(line.slope < other_line.slope):
        time = fractions.Fraction(line.intercept - other_line.intercept, line.slope - other_line.slope)
        return time, line.slope * time + line.intercept
    return None


def sweepline(state, queue):
    while len(queue) != 0:
        heapq.heappop().task.execute(state, queue)


class AreaColumnsState:

    def __init__(self, upper_bounds, lower_bounds):
        self.upper_bounds = upper_bounds
        self.lower_bounds = lower_bounds
        self.upper_bounds_index = 0
        self.lower_bounds_index = 0
        state = []
        queue = []
        start_point = crossing(upper_bounds[0], lower_bounds[0])

    def adv_upper_bound(self):
        self.upper_bounds_indes += 1

    def adv_lower_bound(self):
        self.lower_bounds_index += 1

    def result(self):
        return self.columns


def test_find_columns():
    upper_bounds = [(1, 4), (-1, 4)]
    lower_bounds = [(-1, -3), (1, -3)]
    ac = AreaColumns(upper_bounds, lower_bounds)
    for bound in ac:
        print(bound)


if __name__ == "__main__":
    test_find_columns()
