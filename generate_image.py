import random
import sys
from PIL import Image


def generate_image(size, output_file_name):
    random.seed()
    image = Image.new("RGB", (size, size))
    for i in range(size):
        for j in range(size):
            image.putpixel((i, j), (random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)))
    image.show()
    image.save(output_file_name, "PNG")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: {0} size output_file.png".format(sys.argv[0]))
        sys.exit(1)
    _, size, output_file_name = sys.argv
    generate_image(int(size), output_file_name)
