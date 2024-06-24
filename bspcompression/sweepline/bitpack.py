import array
import struct
import sys

FILENAME = "test.data"
BYTE_LENGTH = 8
BYTE_MASK = 0Xff


# BYTE_MASK = 2 ** BYTE_LENGTH - 1


class BitPackWriter:

    def __init__(self, file_name, verbose=False):
        self.bits_left2write = 0
        self.value_buffer = 0
        self.file_name = file_name
        self.file = None
        self.verbose = verbose
        self.bits_written = 0

    def write(self, value, bit_length):
        self.bits_written += bit_length
        value <<= self.bits_left2write
        self.bits_left2write += bit_length
        self.value_buffer |= value
        byte_values = []
        while self.bits_left2write >= BYTE_LENGTH:
            byte_values.append(self.value_buffer & BYTE_MASK)
            self.value_buffer >>= BYTE_LENGTH
            self.bits_left2write -= BYTE_LENGTH
        self.file.write(bytearray(byte_values))

    def __enter__(self):
        self.file = open(self.file_name, "wb")
        return self

    def close(self):
        self.__exit__(None, None, None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.bits_left2write > 0:
            self.file.write(bytearray([self.value_buffer & BYTE_MASK]))
            # self.bits_left2write = 0
        if self.verbose:
            print(self.bits_written, "bits written to", self.file_name)
        self.file.close()
        # I do not handle the exception here, therefore I do not return True


class BitPackReader:

    def __init__(self, file_name):
        self.buffer_byte = 0
        self.bit_index = BYTE_LENGTH  # becomes 0 when reading a new byte
        self.file_name = file_name
        self.file = None

    def __enter__(self):
        self.file = open(self.file_name, "br")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def read(self, bit_length):
        if self.bit_index > 0:
            byte_list = [self.buffer_byte]
        else:
            byte_list = []
#        print("value bytes:", ["{0:08b}".format(byte) for byte in byte_list])
        bytes2read = (bit_length + self.bit_index - 1) // BYTE_LENGTH
        if bytes2read > 0:
            byte_list = byte_list + list(self.file.read(bytes2read))
            self.buffer_byte = byte_list[-1]
#        print("value bytes:", ["{0:08b}".format(byte) for byte in byte_list])
        return_value = bits_from_bytes(bytes_=byte_list, start=self.bit_index, bit_length=bit_length, order="little")
        self.bit_index = self.bit_index + bit_length - BYTE_LENGTH * bytes2read
        return return_value


    def read_old(self, bit_length):
        value = cut_off_least_significant_and_shift(self.buffer_byte, self.bit_index)
        print("1: val: {0:08b}, buffer: {1:08b}, index: {2}".format(value, self.buffer_byte, self.bit_index))
        value_bytes_number = (bit_length + self.bit_index) // BYTE_LENGTH
        print("number of bytes to read: " , value_bytes_number)
        if value_bytes_number > 0:
            value_bytes = self.file.read(value_bytes_number)
            print("value bytes:", ["{0:08b}".format(byte) for byte in value_bytes])
            for ordinal, infix_byte in enumerate(value_bytes[0:-1]):
                value |= infix_byte << (ordinal * BYTE_LENGTH)
                print("4: value inside loop: {0:b}".format(value))
            self.bit_index += bit_length - BYTE_LENGTH * value_bytes_number
            # value <<= self.bit_index
            print("5: value post loop: {0:b}".format(value))
            self.buffer_byte = value_bytes[-1]
            last_bits = cut_off_most_significant_bits(self.buffer_byte, BYTE_LENGTH - self.bit_index)
            print("5.5: last bits: {0:08b}".format(last_bits))
            value |= last_bits << (bit_length + BYTE_LENGTH * (value_bytes_number - 1) - self.bit_index)
            print("6: value after some bytes read: {0:b}".format(value))
        else:
            self.bit_index += bit_length
            value = cut_off_most_significant_bits(value, BYTE_LENGTH - bit_length)
            print("7: no bytes read: {0:08b}".format(value))
        print("bit_index:", self.bit_index, "; buffer_byte:", "{0:08b}".format(self.buffer_byte))
        return value
        # handle the bytes in between

        #bytes2read = (bit_length - self.bit_index) // BYTE_LENGTH
        # start at the beginning of the byte that may still be in the buffer
        # value = self.buffer_byte >> self.bit_index
        # go through the in-between bytes (if any)
        # value_bytes = self.file.read(bytes2read)
        # for byte in value_bytes:
        #    value <<= BYTE_LENGTH
        #    value |= byte
        # handle the last byte
        #self.bit_index = (self.bit_index + bit_length) % BYTE_LENGTH

    def read_within_byte(self, bit_length):
        value = self.buffer_byte
        mask = BYTE_MASK >> self.bit_index + bit_length
        self.bit_index += bit_length
        value &= mask
        value >>= self.bit_index
        return value


def read_within_byte(buffer_byte, bit_index, bit_length):
    value = buffer_byte
#    print("value: {0:08b}".format(value))
    mask = BYTE_MASK >> (bit_index + bit_length)
#    print("mask: {0:08b}".format(mask))
#    bit_index += bit_length
#    print(bit_length)
    value &= mask
#    print("value & mask: {0:08b}".format(value))
    value >>= bit_index
#    print("value & mask >> bit_index: {0:08b}".format(value))
    return value


def cut_off_least_significant_and_shift(byte, margin):
    return byte >> margin


def cut_off_most_significant_bits(byte, margin):
#    return byte & (BYTE_MASK & (BYTE_MASK >> margin))
    return byte & (BYTE_MASK >> margin)


def read_within_byte_2(buffer_byte, bit_index, bit_length):
    value = cut_off_least_significant_and_shift(buffer_byte, bit_index)
    # go through loop
    value = cut_off_most_significant_bits(value, BYTE_LENGTH - bit_length)
    return value


def bitmask_value(byte, start_bit, end_bit):
    mask = BYTE_MASK
    mask >>= BYTE_LENGTH + start_bit - end_bit
    mask >> start_bit
    return byte >> start_bit


def pack_unpack_struct():
    # Packing data
    # The format string '3i' indicates that we are packing three integers.
    packed_data = struct.pack('3i', 100, 200, 300)
    print("Packed data:", packed_data)

    # Unpacking data
    # The format string '3i' is used again to unpack the data.
    unpacked_data = struct.unpack('3i', packed_data)
    print("Unpacked data:", unpacked_data)


def store_data(data, file_name):
    arr = bytearray(data)
    with open(file_name, "wb") as file:
        file.write(arr)


def recover_data(file_name):
    with open(file_name, "rb") as file:
        return list(file.read())


def test_write_bits():
    with BitPackWriter(FILENAME) as writer:
        for bits in range(1, 16 + 1):
            writer.write(value=1, bit_length=bits)


def test_value_from_bits(bits):
    return 1 + 2 ** (bits - 1)


def test_read_bits():
    with BitPackWriter(FILENAME) as writer:
        for bits in range(2, 16 + 1):
            writer.write(test_value_from_bits(bits), bit_length=bits)
    with BitPackReader(FILENAME) as reader:
        for bits in range(2, 16 + 1):
            number = reader.read(bits)
            print("bits: ",  bits, ", value: ", "{0:08b}".format(number),
                  ", goal: ", "{0:08b}".format(test_value_from_bits(bits)), ", match: ", test_value_from_bits(bits) == number)
            print("============================================================================")


def mask(number, start, bit_size):
    return (number >> start) & ((1 << bit_size) - 1)


def bits_from_bytes(bytes_, start, bit_length, order):
    return mask(int.from_bytes(bytes_, byteorder=order), start, bit_length)


def bits_into_bytes(value, start, bit_length, order):
    answer = value.to_bytes(order) << start
    goal_length = (start + bit_length - 1) // BYTE_LENGTH + 1
    return


def test_read_within_bytes():
    print(read_within_byte(1 + 4 + 64, 2, 2))


def generic_test(string, fun, vargs, kwargs, goal):
    result = fun(*vargs, **kwargs)
    if result == goal:
        print("SUCCESS!!", string, "args:", vargs, kwargs, "result:", result)
    else:
        print("FAILURE!!", string, "args:", vargs, kwargs, "result:", result, "goal:", goal)


def incremental_bytes_test():
    byte_values = list(range(16))
    with BitPackWriter(FILENAME) as writer:
        for byte in byte_values:
            writer.write(byte, bit_length=BYTE_LENGTH)
    with BitPackReader(FILENAME) as reader:
        print( "### eerste", reader.read(4))
        for i in range(15):
            print("###", i, reader.read(8))
        print("### laatste", reader.read(4))


def write_int64_test():
    byte_values = list(range(16))
    with BitPackWriter(FILENAME) as writer:
        for byte in byte_values:
            writer.write(byte, bit_length=64)
    with BitPackReader(FILENAME) as reader:
        for i in range(15):
            print("###", i, reader.read(64))


def trash_test():
    sixteen_ones = [255, 255]      #  "\0xff\0xff"
    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": sixteen_ones, "start": 0, "bit_length": 16, "order": "little"}, goal=2 ** 16 - 1)
    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": sixteen_ones, "start": 4, "bit_length": 8, "order": "little"}, goal=2 ** 8 - 1)

    test_bytes = [255, 0]
    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": test_bytes, "start": 0, "bit_length": 16, "order": "little"}, goal=2 ** 8 - 1)
    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": test_bytes, "start": 4, "bit_length": 8, "order": "little"}, goal=2 ** 4 - 1)

    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": test_bytes, "start": 0, "bit_length": 16, "order": "big"}, goal=2 ** 16 - 2 ** 8)
    generic_test("bits_from_bytes", bits_from_bytes, [],
                 {"bytes_": test_bytes, "start": 4, "bit_length": 8, "order": "big"}, goal=2 ** 8 - 2 ** 4)

    print(cut_off_least_significant_and_shift(BYTE_MASK, margin=4))
    print(cut_off_most_significant_bits(BYTE_MASK, margin=3))
    print(cut_off_least_significant_and_shift(129, margin=1))
    print(cut_off_most_significant_bits(129, margin=2))
    print(read_within_byte_2(255, 2, 2))
    print(read_within_byte_2(129, 2, 4))
    print(read_within_byte_2(129, 0, 4))
    print(read_within_byte_2(129, 4, 4))


def full_range_test(bit_length):
    result = True
    limit = 2 ** bit_length
    with BitPackWriter(FILENAME) as writer:
        for i in range(limit):
            writer.write(i, bit_length)
    with BitPackReader(FILENAME) as reader:
        for i in range(limit):
            val = reader.read(bit_length)
            result &= i == val
    #        print(i, val, i == val)
    return result


def main():
    print("__byte_order:", sys.byteorder)
#    trash_test()
#    store_data([1, 2, 3, 32, 64, 128, 255], FILENAME)
#    recover_data(FILENAME)
#    test_write_bits()
#    incremental_bytes_test()
    print("++++++++++++++++++++++")
#    write_int64_test()
    print("++++++++++++++++++++++")
    test_read_bits()
    print(["{0:08b}".format(byte) for byte in recover_data(FILENAME)])
    #    test_read_within_bytes()
    print("______________________")
    for i in range(16 + 1):
        print(i, i, i, i, i, i, i)
        print(full_range_test(i))


if __name__ == "__main__":
    main()
