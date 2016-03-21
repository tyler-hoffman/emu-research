#! /usr/bin/env python3

from PIL import Image

def get_image_data(filename, count = -1):
    f = open(filename, 'rb')

    def next(num_bytes = 1):
        x = f.read(num_bytes)
        return int.from_bytes(x, byteorder='big')

    magic_number = next(4)

    if count < 0:
        count = next(4)
    else:
        next(4)

    rows = next(4)
    cols = next(4)

    output = [
        [255 - next() for i in range(rows * cols)] for k in range(count)
    ]

    f.close()
    return output, (rows, cols)

def get_labels(filename):

    f = open(filename, 'rb')

    def next(num_bytes = 1):
        x = f.read(num_bytes)
        return int.from_bytes(x, byteorder='big')

    magic_number = next(4)

    count = next(4)
    output = [next() for i in range(count)]

    f.close()
    return output

if __name__ == '__main__':
    label_file = 'train-labels-idx1-ubyte'
    image_file = 'train-images-idx3-ubyte'

    labels = get_labels(label_file)
    image_data, size = get_image_data(image_file, 2000)

    test_indices = [i for i in range(10)]
    for i in test_indices:
        print(labels[i])
        im = Image.new('L', size)
        im.putdata(image_data[i])
        im.show()
