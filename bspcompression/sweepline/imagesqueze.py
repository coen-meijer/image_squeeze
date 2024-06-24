import math

import numpy as np
from PIL import Image
from dataclasses import dataclass

from sweepline.bitpack import BitPackWriter, BitPackReader

SQUARE_SIDE = 3
MAX_LEVELS = 5

IMAGE_FILE = r"Z:\downloads\how-ot-make-picture-black-and-white-after.jpg"
CAT = r"Z:\downloads\Grayscale_Cat(1).jpg"
X_RAY = r"Z:\downloads\xray.webp"
X_RAY_DETAIL = r"Z:\downloads\xray_detail.PNG"
SCREEN = r"Z:\downloads\screen.png"
DRAWING = r"Z:\downloads\draw.jpg"
ANT = r"Z:\downloads\ant.jpg"
PIET = r"z:\downloads\piet-grijze-boom.jpg"
BLANCO = r"z:\downloads\blanco.jpg"
KLEIN = r"z:\downloads\klein.png"
GROOT = r"z:\downloads\groot.png"

PIC = X_RAY
OUT = r"Z:\downloads\out.sqz"

TMP_PREFIX = r"Z:\downloads\tmp" + "\\"
EXTENSION = ".png"

BETWEEN = 150

PALETTE = [
    [0, 0, 0],
    [0, 0, BETWEEN],
    [0, 0, 255],
    [0, BETWEEN, BETWEEN],
    [0, 255, 0],
    [127, BETWEEN, 0],
    [255, 255, 0],
    [255, 255, BETWEEN],
    [255, 255, 255]
]

"""
A module that aims to reduce space to store pictures by 
taking a square of pixels and recording a minimum and maximum
than storing the difference between the two levels.
These numbers should be relatively small, so with a good 
frequency table they should be able to be compressible
"""


@dataclass
class IntRange:
    minimum: int
    maximum: int

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def count(self):
        return self.maximum - self.minimum + 1


BYTE_RANGE = IntRange(0, 255)


def interval_from_arrays(minimum_array, maximum_array, index):
    return IntRange(minimum_array[index].item(), maximum_array[index].item())


def array_squeeze(color_values, side):
    if isinstance(color_values, tuple):
        color_values_min = color_values[0]
        color_values_max = color_values[1]
    elif isinstance(color_values, dict):
        color_values_min = color_values['minima']
        color_values_max = color_values['maxima']
    else:
        color_values_min = color_values
        color_values_max = color_values
    shape = color_values_min.shape
    # print(shape)
    # width = shape[0]
    # height = shape[1]
    width, height = shape
    color_range = 255  # todo: Look at deriving this from the file.
    level_table_shape = ((width - 1) // side + 1, (height - 1) // side + 1)
    # print(level_table_shape)
    min_layer = np.full(level_table_shape, fill_value=color_range, dtype=np.ubyte)
    max_layer = np.zeros(level_table_shape, dtype=np.ubyte)
    for i in range(side):
        for j in range(side):
            min_pixels = color_values_min[j:width:side, i:height:side]
            max_pixels = color_values_max[j:width:side, i:height:side]
            selection_min = slice(0, min_pixels.shape[0]), slice(0, min_pixels.shape[1])
            selection_max = slice(0, max_pixels.shape[0]), slice(0, max_pixels.shape[1])
            min_layer[selection_min] = np.fmin(min_layer[selection_min], min_pixels)
            max_layer[selection_max] = np.fmax(max_layer[selection_max], max_pixels)
    return {"minima": min_layer, "maxima": max_layer}


def array2grayscale(array):
    return Image.fromarray(array, "L")


def whole_bit_difference_im(max_im, min_im):
    dif_log = np.array(np.ceil(np.log2(max_im - min_im + 1))).astype(np.uint8)
    print(np.average(dif_log))
    dif_log = dif_log * 31
    im = Image.fromarray(dif_log, "L")
    return im


def main():
    im = Image.open(PIC)
    im.show()
    image_data = np.array(im.convert("L"))
    store_grayscale_sqz(image_data, OUT)
    image_retrieved_data = read_grayscale_sqz(IMAGE_FILE)
    image_retrieved = array2grayscale(image_retrieved_data)
    image_retrieved.show(title="main")
    print(image_data.shape[0] * image_data.shape[1] * 8, "pixels * 8")
    #  difference_im = array2grayscale(image_data - image_retrieved_data)
    #  difference_im.show()
    if False:
        min_array, max_array = array_squeeze(image_data, SQUARE_SIDE)
        max_im = array2grayscale(max_array)
        min_im = array2grayscale(min_array)
        dif_im = whole_bit_difference_im(max_array, min_array)
        im.show()
        max_im.show()
        min_im.show()
        dif_im.show()
        min_min, min_max = array_squeeze(min_array, SQUARE_SIDE)
        array2grayscale(min_min).show()
        array2grayscale(min_max).show()
        whole_bit_difference_im(min_max, min_min).show()


# Hoe en waarom van minimum en maximum opslaan in een getal
#
# In een computer ben je altijd bezig met een representatie
# van iets in bits. Hoe meer combinaties er mogelijk zijn in het
# gene dat je probeert te representeren.
# hoe meer bits er nodig zijn om dat te doen.
# dinges


def range_in_range_bits(interval: IntRange):
    return int.bit_length(interval.count() * (interval.count() + 1) // 2 - 1)


def print_number_to_range_table(interval: IntRange):
    max_len = 1
    table_row = ["."] * (interval.maximum + 1)
    table = []
    for i in range(interval.maximum + 1):
        table.append(list(table_row))
    triangle_number = interval.count() * (interval.count() + 1) // 2
    for i in range(triangle_number):
        contained_interval = number_to_min_max(interval, i)
        cell_string = str(i)
        max_len = max(max_len, len(cell_string))
        table[contained_interval.minimum][contained_interval.maximum] = cell_string
    print_table(table, max_len)


def print_number_to_range_to_index_table(interval: IntRange):
    max_len = 1
    table_row = ["."] * (interval.maximum + 1)
    table = []
    for i in range(interval.maximum + 1):
        table.append(list(table_row))
    triangle_number = interval.count() * (interval.count() + 1) // 2
    for i in range(triangle_number):
        contained_interval = number_to_min_max(interval, i)
        cell_string = "(" + str(contained_interval.maximum) + ", " + str(contained_interval.minimum) + ")"
        max_len = max(max_len, len(cell_string))
        table[contained_interval.minimum][contained_interval.maximum] = cell_string
    print_table(table, max_len)


def print_table(table, max_len):
    for line in table:
        line_sting = ""
        for cell in line:
            line_sting += cell.rjust(max_len + 1)
        print(line_sting)


def number_in_range_bits(interval: IntRange):
    return int.bit_length(interval.count() - 1)


def min_max_to_number(enclosing_interval: IntRange, contained_interval: IntRange):
    range_size = enclosing_interval.count()
    combinations_count = (range_size * (range_size + 1)) // 2
    max_offset = contained_interval.maximum - enclosing_interval.minimum
    min_offset = contained_interval.minimum - enclosing_interval.minimum
    answer = max_offset + range_size * min_offset
    if answer >= combinations_count:
        answer = range_size * (range_size + 1) - answer - 1
    return answer


def number_to_min_max(containing_interval, number) -> IntRange:
    range_size = containing_interval.count()
    maximum = number % range_size
    minimum = number // range_size
    if maximum < minimum:
        maximum = range_size - maximum - 1
        minimum = range_size - minimum
    return IntRange(minimum + containing_interval.minimum, maximum + containing_interval.minimum)


def save_array_as_grayscale(array, title):
    array2grayscale(array).save(TMP_PREFIX + title + str(array.shape) + EXTENSION)


def store_grayscale_sqz(array, file_name):
    show_images = True
    with BitPackWriter(file_name, verbose=True) as writer:
        writer.write(SQUARE_SIDE, 8)
        writer.write(MAX_LEVELS, 8)
        # colour depth(s)?
        horizontal, vertical = array.shape
        dimension_bits = int.bit_length(max(horizontal, vertical))
        writer.write(dimension_bits, 8)
        writer.write(horizontal, dimension_bits)
        writer.write(vertical, dimension_bits)
        current_level = {'minima': array, 'maxima': array}
        levels = [current_level]
        # while horizontal >= TOP_LEVEL_MAX_DIMENSION or vertical >= TOP_LEVEL_MAX_DIMENSION:
        for i in range(1, MAX_LEVELS):
            new_level = array_squeeze(current_level, SQUARE_SIDE)
            if show_images:
                save_array_as_grayscale(new_level["minima"], "store minima level" + str(i))
                save_array_as_grayscale(new_level["maxima"], "store maxima level" + str(i))
            levels.append(new_level)
            current_level = new_level
        # todo: store top level max dimension
        # todo: store square_size
        levels.reverse()
        histogram = layers_histogram(levels)
        print(histogram)
        # store the highest, smallest level
        horizontal, vertical = levels[0]['minima'].shape
        for j in range(vertical):
            for i in range(horizontal):
                writer.write(min_max_to_number(
                    enclosing_interval=BYTE_RANGE,
                    contained_interval=interval_from_arrays(levels[0]['minima'], levels[0]['maxima'], (i, j))),
                    bit_length=range_in_range_bits(BYTE_RANGE))
        # now we have all levels, we start at the top level and for each level below we
        # store the range in its area using the range given by the range just above it
        for above, below in zip(levels[0:-2], levels[1:-1]):
            horizontal, vertical = below['minima'].shape
            for j in range(vertical):
                for i in range(horizontal):
                    enclosing = interval_from_arrays(above['minima'], above['maxima'],
                                                     (i // SQUARE_SIDE, j // SQUARE_SIDE))
                    contained = interval_from_arrays(below['minima'], below['maxima'], (i, j))
                    interval_number = min_max_to_number(
                        enclosing_interval=enclosing,
                        contained_interval=contained)
                    writer.write(interval_number, range_in_range_bits(enclosing))
        above = levels[-2]
        below = levels[-1]
        horizontal, vertical = below['minima'].shape
        for j in range(vertical):
            for i in range(horizontal):
                above_index = i // SQUARE_SIDE, j // SQUARE_SIDE
                value = below["minima"][i, j] - above['minima'][above_index]
                bit_length = int.bit_length(above['maxima'][above_index].item() -
                                            above['minima'][above_index].item())
                writer.write(value=value, bit_length=bit_length)


def level_dimensions_calc(maximum, hor, vert, side) -> list:
    answer = [(hor, vert)]
    for i in range(maximum - 1):
        hor = (hor - 1) // side + 1
        vert = (vert - 1) // side + 1
        answer.append((hor, vert))
    answer.reverse()
    return answer


def read_grayscale_sqz(file_name):
    store_image = True
    with BitPackReader(file_name) as reader:
        square_side = reader.read(8)
        max_levels = reader.read(8)
        dimension_bits = reader.read(8)
        horizontal = reader.read(dimension_bits)
        vertical = reader.read(dimension_bits)
        level_dimensions = level_dimensions_calc(max_levels, horizontal, vertical, square_side)
        above_level_min = np.zeros(level_dimensions[0], np.ubyte)
        above_level_max = np.zeros(level_dimensions[0], np.ubyte)

        for j in range(level_dimensions[0][1]):
            for i in range(level_dimensions[0][0]):
                range_number = reader.read(range_in_range_bits(BYTE_RANGE))
                hue_range = number_to_min_max(BYTE_RANGE, range_number)
                above_level_min[i, j] = hue_range.minimum
                above_level_max[i, j] = hue_range.maximum
        if store_image:
            save_array_as_grayscale(above_level_min, "top level min read")
            save_array_as_grayscale(above_level_max, "top level max read")
        # print("level dimensions", level_dimensions)
        for below_dim in level_dimensions[1:-1]:
            below_min_array = np.zeros(below_dim, np.ubyte)
            below_max_array = np.zeros(below_dim, np.ubyte)
            for j in range(below_dim[1]):
                for i in range(below_dim[0]):
                    enclosing_interval = interval_from_arrays(above_level_min, above_level_max,
                                                              (i // square_side, j // square_side))
                    # print("outer interval" , enclosing_interval, "on coordinates", i // square_side, j // square_side)
                    range_number = reader.read(range_in_range_bits(enclosing_interval))
                    hue_range = number_to_min_max(enclosing_interval, range_number)
                    # print("inner interval", hue_range, "at coordinates", i, j, "from number", range_number)
                    below_min_array[i, j] = hue_range.minimum
                    below_max_array[i, j] = hue_range.maximum
            if store_image:
                save_array_as_grayscale(below_min_array, "min layer read, dimensions")
                save_array_as_grayscale(below_max_array, "max layer read, dimensions")
            above_level_min = below_min_array
            above_level_max = below_max_array
        ground_level = np.zeros((horizontal, vertical), np.ubyte)
        for j in range(level_dimensions[-1][1]):
            for i in range(level_dimensions[-1][0]):
                hue_range = interval_from_arrays(above_level_min, above_level_max, (i // square_side, j // square_side))
                hue_minimum = above_level_min[i // square_side, j // square_side]
                read_value = reader.read(number_in_range_bits(hue_range))
                value = read_value + hue_minimum
                # if value > 255 or value < 0:
                    # print("value out of range!! ", read_value , value, hue_range, number_in_range_bits(hue_range))
                ground_level[i, j] = value
        if store_image:
            save_array_as_grayscale(ground_level, "ground level read")
    return ground_level


def layers_histogram(layers, range_max=256):
    # make a histogram
    histogram = []
    for i in range(range_max):
        histogram.append(0)
    # go through all the layers
    for layer in layers[:-1]:
        for limit in ['minima', 'maxima']:
            for byte in np.nditer(layer[limit]):
                histogram[byte] += 1
    # add the ground layer
    for byte in np.nditer(layers[-1]['minima']):
        histogram[byte] += 1
    return histogram


def number_min_max_test():
    count = 0
    mother_range = IntRange(0, 7)
    for minimum in range(8):
        for maximum in range(minimum, 8):
            containded = IntRange(minimum, maximum)
            print(containded)
            print_number_to_range_table(containded)
            print_number_to_range_to_index_table(containded)
    for j in range(0):
        triangle_number = (j + 2) * (j + 1) // 2
        interval = IntRange(0, j)
        print(">>>>", interval, "<<<<")
        print_number_to_range_table(interval)
        print_number_to_range_to_index_table(interval)
        for i in range(0):  # triangle_number):
            reach = number_to_min_max(interval, i)
            number = min_max_to_number(interval, reach)
            print(i, reach, number)
            count += 1
            if i != number:
                print("???")
        print("======================================")
    print(count)


if __name__ == "__main__":
    number_min_max_test()
    main()

# overwegingen

# ik kan dit uitbreiden naar meer dingen.
# 
