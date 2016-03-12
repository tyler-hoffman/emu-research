#! /usr/bin/env python3

from scaling import crop_and_scale
from PIL import Image

def avg(array):
    return sum(array) / len(array)

def normalize(values):
    upper = max(values)
    return [v / upper for v in values]

def quantize(values, states):
    upper = max(values) + 1
    step = upper / states
    return [int(v / step) for v in values]


def get_values(image, size, states = 8):
    image = crop_and_scale(image, size, 0)

    pixels = [avg(p) for p in list(image.getdata())]
    pixels = quantize(pixels, states)
    return pixels

if __name__ == '__main__':
    from sys import argv
    import os

    if len(argv) < 3:
        print('use: ./zoningwriter.py <image_directory> <zones>')
    else:
        path = argv[1]
        size = int(argv[2])
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('jpeg'):
                    label = f[0]
                    image = Image.open(os.path.join(root, f))
                    values = get_values(image, (size, size))
                    print(label + ' ' + ' '.join(str(x) for x in values))
