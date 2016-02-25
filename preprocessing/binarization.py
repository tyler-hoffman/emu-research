#! /usr/bin/env python3

from PIL import Image, ImageEnhance

identity = lambda x: x

def to_grid(img, f = identity):
    '''Convert an image to a 2d array.
    f -- is the mapping function. Should take one parameter: (r, g, b)
    Note: This is painfully slow :(
    '''
    w, h = img.size
    pixel_data = list(img.getdata())
    grid = [[f(pixel_data[x + w * y]) for x in range(w)] for y in range(h)]

    for y in range(h):
        for x in range(w):
            grid[y][x] = f(pixel_data[x + w * y])
    return grid

def to_img(grid, f = identity, mode = '1'):
    '''Convert a 2d array to an image
    grid -- the 2d array
    mode -- PIL mode ('1' for b/w, 'RGB' for rgb, etc)
    f -- transformation function
    '''
    h = len(grid)
    w = len(grid[0])
    img = Image.new(mode, (w, h), 0)

    for y in range(h):
        for x in range(w):
            img.putpixel((x, y), f(grid[y][x]))

    return img

def to_binary_grid(image, threshold):
    return to_grid(image, lambda p: 1 if sum(p) > threshold else 0)

def image_to_binary(image):
    return image.convert('1', None, False)

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 3:
        print('use: ./binarization.py <image location> <contrast (typically > 1)>')
    else:
        image = Image.open(argv[1])
        contrast = float(argv[2])
        #enh = ImageEnhance.Contrast(image)
        #image = enh.enhance(contrast)

        matrix = (
            contrast, 0, 0, 0,
            0, contrast, 0, 0,
            0, 0, contrast, 0
        )
        print(image.mode)
        image = image.convert('RGB', matrix)

        image = image_to_binary(image)
        image.show()
