#! /usr/bin/env python3

from PIL import Image

avg = lambda l: l if isinstance(l, int) else sum(l) / len(l)
is_dark = lambda p_colors: avg(p_colors) < 100

def get_bounds(image, f = is_dark):
    ''' Get the bounds of meaningful data from an image
    image -- The image
    f -- filter function; takes a tuple of rgb colors
        and must return a boolean value for if the pixel has data
    '''
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

def crop_and_scale(image, size, border = 1, f = is_dark, border_color = 0xffffff):
    ''' Create a cropped and scaled version of an image
    image -- The image
    size -- The size of the image to return
    f -- filter function for meaningful pixels
    border -- border thickness
    border_color -- color for border
    '''

    bounds = get_bounds(image, f)
    output = Image.new(image.mode, size, 0xffffff)
    image = image.crop(bounds)

    adjusted_size = (size[0] - 2 * border, size[1] - 2 * border)
    image = image.resize(adjusted_size, Image.ANTIALIAS)
    output.paste(image, (border, border))

    return output

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print('use: ./scaling.py <image path> (<size>)')
    else:
        image = Image.open(argv[1])
        if len(argv) > 2:
            size = (int(argv[2]), int(argv[2]))
        else:
            size = (800, 800)
        (crop_and_scale(image, size, 0)
                .resize((400, 400))
                .show())
