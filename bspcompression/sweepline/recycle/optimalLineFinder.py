import math
import heapq
from enum import Enum
import numpy


class ColumnEvent(Enum):
    NEW_COLUMN = 1
    BOUND_CHANGE_UP = 2
    BOUND_CHANGE_DOWN = 3
    AREA_CLOSE = 4

    def __lt__(self, other):
        return self.value < other.value


class Ref:
    # used to do pass by reference

    def __init__(self, val):
        self.val = val


class Bound:

    def __init__(self, line_list):
        self.line_list = line_list
        self.index = 0

    def get_line(self):
        return self.line_list[self.index]

    def line_val(self, x):
        line = self.line_list[self.index]
        return line[0] * x + line[1]

    def next_line(self):
        self.index += 1

    def on_last_line(self):
        if self.index == len(self.line_list) - 1:
            return True
        else :
            return False

    def next_event(self):
        line = self.line_list[self.index]
        next_line = self.line_list[self.index + 1]
        return find_intersection(line, next_line)

    def last_line(self):
        return self.line_list[-1]

    def divide_index(self, new_line):
        separation_index = 0
        while True:
            if separation_index >= self.line_list - 1 :
                next_own_intersect = find_intersection(self.line_list[separation_index], self.line_list[separation_index])
                seperator_intersect = find_intersection(self.line_list[separation_index], new_line)
                if seperator_intersect < next_own_intersect:
                    return separation_index
            else :  # On the last line.
                if new_line[0] == self.line_list[separation_index][0]:
                    return None
                else:
                    return separation_index


def find_intersection(line, intersector):
    a = line[0] - intersector[0]
    b = line[1] - intersector[1]
    return -b / a


def find_bound_event(relevant_column_event, bound_list, opposite_bound_list):
    if bound_list.on_last_line():
        return find_intersection(bound_list.last_line(), opposite_bound_list.last_line()), ColumnEvent.AREA_CLOSE
    else :
        return bound_list.next_event(), relevant_column_event


def find_columns(bounds):
    # its own little sweep line algorithm
    # we draw an imaginary vertical line, and we sweep it across the area
    # along the way we
    result = []
    upper_bounds = Bound(bounds[0])
    lower_bounds = Bound(bounds[1])
    start = find_intersection(upper_bounds.get_line(), lower_bounds.get_line())
    column_x = math.ceil(start)
    next_column_x = column_x + 1
    event_queue = []
    heapq.heappush(event_queue, (next_column_x, ColumnEvent.NEW_COLUMN))
    heapq.heappush(event_queue,
                   find_bound_event(ColumnEvent.BOUND_CHANGE_UP, upper_bounds, lower_bounds))
    heapq.heappush(event_queue,
                   find_bound_event(ColumnEvent.BOUND_CHANGE_DOWN, lower_bounds, upper_bounds))
    while continue_flag:
        print(f"{event_queue}")
        match event_queue[0]:
            case (_, ColumnEvent.AREA_CLOSE):
                break
            case (x, ColumnEvent.NEW_COLUMN):

                column_segment = x, (
                    math.ceil(lower_bounds.line_val(x)),
                    math.ceil(upper_bounds.line_val(x))
                )
                result.append(column_segment)
                heapq.heappushpop(event_queue, (x + 1, ColumnEvent.NEW_COLUMN))

            case (x, ColumnEvent.BOUND_CHANGE_UP):
                heapq.heappushpop(event_queue, find_bound_event(ColumnEvent.BOUND_CHANGE_UP,
                                                                upper_bounds, lower_bounds))
                print(f"upper_bounds: {upper_bounds.index}. next_line(). {x}")
                upper_bounds.next_line()

            case (_, ColumnEvent.BOUND_CHANGE_DOWN):
                heapq.heappushpop(event_queue, find_bound_event(ColumnEvent.BOUND_CHANGE_DOWN,
                                                                lower_bounds, upper_bounds))
                print(f"lower_bounds: {lower_bounds.index}. next_line(). {x}")
                lower_bounds.next_line()

    return result


def test_find_columns():
    upper_bounds = [(1, 3), (-1, 3)]
    lower_bounds = [(-1, -3), (1, -3)]
    print(find_columns((upper_bounds, lower_bounds)))


if __name__ == "__main__":
    test_find_columns()
