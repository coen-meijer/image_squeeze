from enum import Enum
import heapq
import math


class PixelColumnEvent(Enum):
    COLUMN = 1
    UPPER_BOUND_CHANGE = 2
    LOWER_BOUND_CHANGE = 3
    END = 4

    def __lt__(self, other):
        return False  # all kinds are equal.


def intersect(line, other):
    result_slope = line[0] - other[0]
    result_constant = line[1] - other[1]
    return -result_constant / result_slope


def line_at(line, time):
    return time * line[0] + line[1]


def area_columns(upper_bounds, lower_bounds):
    """
    takes two lists of lines and outputs the intervals that fall between those lines
    """
    result = []
    queue = []
    heapq.heappush(queue, (-math.inf, PixelColumnEvent.LOWER_BOUND_CHANGE))
    heapq.heappush(queue, (-math.inf, PixelColumnEvent.UPPER_BOUND_CHANGE))
    heapq.heappush(queue, (math.ceil(intersect(upper_bounds[0], lower_bounds[0])), PixelColumnEvent.COLUMN))
    index_upper_bound, index_lower_bound = -1, -1  # will

    while len(queue) > 0:
        print(queue)
        match(heapq.heappop(queue)):
            case _, PixelColumnEvent.UPPER_BOUND_CHANGE:
                index_upper_bound += 1
                upper_line = upper_bounds[index_upper_bound]
                if index_upper_bound + 1 < len(upper_bounds):
                    heapq.heappush(queue,
                                   (intersect(upper_line, upper_bounds[index_upper_bound + 1]),
                                    PixelColumnEvent.UPPER_BOUND_CHANGE))

            case _, PixelColumnEvent.LOWER_BOUND_CHANGE:
                index_lower_bound += 1
                lower_line = lower_bounds[index_lower_bound]
                if index_lower_bound + 1 < len(lower_bounds):
                    heapq.heappush(queue, (intersect(lower_line, lower_bounds[index_lower_bound + 1]),
                                           PixelColumnEvent.LOWER_BOUND_CHANGE))
                else:
                    heapq.heappush(queue, (intersect(upper_bounds[-1], lower_bounds[-1]), PixelColumnEvent.END))

            case _, PixelColumnEvent.END:
                queue = []  # stop

            case time, PixelColumnEvent.COLUMN:
                result.append((math.ceil(line_at(lower_line, time)),
                               math.ceil(line_at(upper_line, time))))
                heapq.heappush(queue, (time + 1, PixelColumnEvent.COLUMN))
    return result


def test_find_columns():
    upper_bounds = [(1, 3), (-1, 3)]
    lower_bounds = [(-1, -3), (1, -3)]
    ac = area_columns(upper_bounds, lower_bounds)
    print(ac)


def main():
    test_find_columns()


if __name__ == "__main__":
    main()
