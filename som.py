import math
import random
import sys
from PIL import Image


# Some helper functions to perform operations on tuples as if they were vectors
# (because I'm too lazy to write a proper Vector class or look for a 3rd-party
# library).
def vadd(a, b):
    # vadd((1, 2, 3), (2, 1, 3)) -> (3, 3, 6)
    return tuple([p[0] + p[1] for p in zip(a, b)])
def vsub(a, b):
    # vsub((1, 2, 3), (2, 1, 3)) -> (-1, 1, 0)
    return tuple([p[0] + p[1] for p in zip(a, b)])
def vmuls(a, s):
    # vmuls((1, 2, 3), 2.0) -> (2.0, 4.0, 6.0)
    return tuple([i * s for i in a])


# A simple class to encapsulate a pixel's position + its color.
class Point:
    def __init__(self, pos, color):
        self.color = color
        self.pos = pos


# Buffer is proxy class to a list, with some additional methods to access it as
# a 2D matrix (get, set).
# It assumes that the given list represents a square image. Therefore `stride`
# is the weight or height of the image.
class Buffer:
    def __init__(self, lst):
        self.lst = lst
        self.stride = int(math.sqrt(len(lst)))

    def get(self, x, y):
        return self.lst[x * self.stride + y]

    def set(self, x, y, value):
        self.lst[x * self.stride + y] = value

    def get_random(self):
        return self.get(random.randint(0, self.stride - 1),
                        random.randint(0, self.stride - 1))

    def __getitem__(self, k):
        return self.lst[k]

    def __setitem__(self, k, v):
        self.lst[k] = v

    def __len__(self):
        return len(self.lst)


# Compute the euclidean distance between two positions.
def distance(a, b):
    return math.sqrt(sum([pow(c[0] - c[1], 2) for c in zip(a, b)]))


# Find out one of the best matching neuron for the given pixel.
# "The best" is defined in term of euclidean distance in the RGB colorspace.
# A good improvement would be to use the HSL space.
def get_best_matching(pix, weights):
    matches = []
    maxdist = None
    for x in range(weights.stride):
        for y in range(weights.stride):
            color = weights.get(x, y)
            d = distance(pix, color)
            if maxdist is None:
                matches.append(Point((x, y), color))
                maxdist = d
            elif d < maxdist:
                matches = [Point((x, y), color)]
                maxdist = d
            elif d == maxdist:
                matches.append(Point((x, y), color))
    return random.choice(matches)


# Update the weights of the neurons around a center one, using the pixel `pix`
# for the iteration `time` and limiting to `base_radius`.
def update_neighbors(weights, point, pix, time, base_radius):
    # The actual radius decreases with time. The / 2.0 is here to speed things
    # up at the beginning
    radius = int(base_radius * (1 - time) / 2.0)
    if radius <= 0:
        return
    center = point.pos
    # For every neuron in the radius (note: we are iterating over a square here,
    # to an actual circle).
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            where = vadd(center, (dx, dy))
            if min(where) < 0 or max(where) >= weights.stride:
                continue
            d = distance(where, center) / radius
            # A gaussian funciton is used to weight the amount of information
            # the neuron should absorb.
            scale = math.exp(-pow(d,2)/0.15)/(time * 4 + 1)
            # The new neuron is a weighted sum of the old one, and the given
            # pixel, using scale as a weight factor.
            new = vadd(vmuls(pix, scale), vmuls(point.color, 1.0 - scale))
            weights.set(where[0], where[1], tuple(map(int, new)))


def run(input_file_name, output_file_name):
    # Maximum number of iterations to perform.
    max_iter = 1000
    time_inc = 1.0 / max_iter
    in_image = Image.open(input_file_name)
    size = in_image.size
    # Default radius. Keep it large so that the first given points can move
    # everywhere.
    base_radius = size[0]

    buff = Buffer(list(in_image.getdata()))


    # initialize neurons at random
    weights = Buffer([0]*(size[0] * size[1]))
    for i in range(size[0] * size[1]):
        weights[i] = (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 255))

    time = 0
    # Algorithm's main loop
    while time <= 1.0:
        print(time)
        pix = buff.get_random()
        best_point = get_best_matching(pix, weights)
        update_neighbors(weights, best_point, pix, time, base_radius)
        time += time_inc


    # Write out the image
    out_image = Image.new("RGB", size)
    # XXX this is highly inefficient, but I don't want to fight with PIL right
    # now.
    for x in range(size[0]):
        for y in range(size[1]):
            out_image.putpixel((x, y), weights.get(x, y))
    out_image.save(output_file_name)
    out_image.show()


if __name__ == '__main__':
    random.seed()
    if len(sys.argv) != 3:
        print("Uage: {0} input_file.png output_file.png".format(sys.argv[0]))
        sys.exit(1)
    _, input_file_name, output_file_name = sys.argv
    run(input_file_name, output_file_name)
