from PIL import Image
import numpy as np

im = Image.open("./MoSe2BNMoSe2/default.png")

[xs, ys] = im.size

def find_range(r, g, b):
    return max(r, g, b) - min(r, g, b)

for i in range(xs):
    for j in range (ys):
        location = (i,j)
        pixel = im.getpixel(location)
        [r, g, b, t] = pixel
        if find_range(r, g, b) < 10:
            im.putpixel(location, (0, 0, 0))
        else:
            if b > 120 and r < 120 and g < 120:
                im.putpixel(location, (0, 0, 255))
            else:
                im.putpixel(location, (0, 0, 0))

im.show()


im.save("./MoSe2BNMoSe2/blue.png")