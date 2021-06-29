from PIL import Image
import numpy as np

im = Image.open("./artificial_shear_iso.png")

[xs, ys] = im.size

def find_range(r, g, b):
    return max(r, g, b) - min(r, g, b)

def convert(i):
    if i > 120:
        return 255
    else:
        return 0

cTRESHOLD = 100

for i in range(xs):
    for j in range (ys):
        location = (i,j)
        pixel = im.getpixel(location)

        red = pixel[0]
        green = pixel[1]
        blue = pixel[2]

        new_r = min(255 - green, 255 - blue)
        new_g = min(255 - red, 255 - blue)
        new_b = min(255 - red, 255 - green)

        if max(new_r, new_g, new_b) - min(new_r, new_g, new_b) < cTRESHOLD:
            new_r = convert(new_r)
            new_g = convert(new_g)
            new_b = convert(new_b)
        else:
            if max(new_r, new_g, new_b) == new_r:
                new_r, new_g, new_b = 255, 0, 0
            elif max(new_r, new_g, new_b) == new_g:
                new_r, new_g, new_b = 0, 255, 0
            elif max(new_r, new_g, new_b) == new_b:
                new_r, new_g, new_b = 0, 0, 255

        im.putpixel(location, (new_r, new_g, new_b))
        

im.show()

im.save("./artificial_shear_iso_inverted.PNG")