#! /usr/bin/env python3

avg = lambda l: sum(l) / len(l)
is_dark = lambda p_colors: avg(p_colors) < 100

def get_bounds(image, f = is_dark):
    pixel_data = list(image.getdata())
    w = image.width
    x_min = 0
    y_min = 0
    x_max = image.width
    y_max = image.height

    def find_first(range_a, range_b, index):
        for a in range_a:
            for b in range_b:
                if f(pixel_data[index(a, b)]):
                    return a

    for_row = lambda x, y: x + y * w
    for_col = lambda y, x: x + y * w

    x_min = find_first(range(image.width), range(image.height), for_row)
    x_max = find_first(range(image.width - 1, 0, -1), range(image.height), for_row)
    y_min = find_first(range(image.height), range(image.width), for_col)
    y_max = find_first(range(image.height - 1, 0, -1), range(image.width), for_col)

    return (x_min, y_min, x_max, y_max)

def scale(image, size, f = is_dark, border = 2, background_color = 0xffffff):

    bounds = get_bounds(image, f)
    output = Image.new(image.mode, size, 0xffffff)
    image = image.crop(bounds)

    adjusted_size = (size[0] - 2 * border, size[1] - 2 * border)
    image = image.resize(adjusted_size, Image.ANTIALIAS)
    output.paste(image, (border, border))

    return output

if __name__ == '__main__':
    from sys import argv
    from PIL import Image

    if len(argv) < 2:
        print('use: ./scaling.py <image path>')
    else:
        size = (800, 800)
        image = Image.open(argv[1])
        image = image.resize(size, Image.ANTIALIAS)
        image.show()

        scale(image, (400, 400)).show()
