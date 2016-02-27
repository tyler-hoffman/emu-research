#! /usr/bin/env python3

def skeletonize(grid):
    '''Apply thinning to a binary grid representation of an image.
    This uses a Thinning algorithm designed by T.Y. Zhang
    and C. Y. Suen.

    grid -- 2d array of 0s and 1s
    '''

    width = len(grid[0])
    height = len(grid)

    def get_pixel(row, col):
        if row < 0 or row == height or col < 0 or col == width:
            return 0
        else:
            return grid[row][col]

    def list_neighbors(row, col):
        neighbors = [0 for i in range(8)]
        neighbors[0] = get_pixel(row - 1, col)
        neighbors[1] = get_pixel(row - 1, col + 1)
        neighbors[2] = get_pixel(row, col + 1)
        neighbors[3] = get_pixel(row + 1, col + 1)
        neighbors[4] = get_pixel(row + 1, col)
        neighbors[5] = get_pixel(row + 1, col - 1)
        neighbors[6] = get_pixel(row, col - 1)
        neighbors[7] = get_pixel(row - 1, col - 1)
        return neighbors

    def count_neighbors(neighbors):
        count = 0
        for n in neighbors:
            if n:
                count += 1
        return count

    def count_0_to_1(neighbors):
        count = 0

        prev = neighbors[-1]
        for n in neighbors:
            if n and not prev:
                count += 1
            prev = n

        return count

    def neighbor_product(neighbors, indices):
        product = 1
        for i in indices:
            product *= neighbors[i - 2]
        return product

    def iteration(n, oddIteration):
        if oddIteration:
            if (neighbor_product(n, (2, 4, 6))
                    or neighbor_product(n, (4, 6, 8))):
                return False
            else:
                return True
        else:
            if (neighbor_product(n, (2, 4, 8))
                    or neighbor_product(n, (2, 6, 8))):
                return False
            else:
                return True

    changed = True
    oddIteration = False
    i = 0
    while changed:
        to_delete = set()
        i += 1

        changed = False
        oddIteration = not oddIteration

        for row in range(height):
            for col in range(width):
                if grid[row][col]:
                    n = list_neighbors(row, col)
                    n_count = count_neighbors(n)
                    if (2 <= n_count and n_count <= 6
                            and count_0_to_1(n) == 1
                            and iteration(n, oddIteration)):
                        to_delete.add((row, col))

        changed = len(to_delete) > 0
        for (row, col) in to_delete:
            grid[row][col] = 0

if __name__ == '__main__':
    import binarization
    from sys import argv
    from PIL import Image

    if len(argv) < 2:
        print('use: ./skeletonize.py <image path>')
    else:

        inverse = lambda i: 0 if i else 1

        image = Image.open(argv[1])
        image = binarization.image_to_binary(image)
        image.show()
        grid = binarization.to_grid(image, inverse)
        grid = [row[:] for row in grid]

        skeletonize(grid)
        binarization.to_img(grid, inverse).show()
