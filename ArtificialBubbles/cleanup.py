from PIL import Image
import numpy as np

im = Image.open("./artificial_2bubbles.jpg")

[r, g, b] = im.split() 

[xs, ys] = im.size

def find_range(r, g, b):
    return max(r, g, b) - min(r, g, b)

cTRESHOLD = 50

for i in range(xs):
    for j in range (ys):
        location = (i,j)
        pixel = im.getpixel(location)
        mean = np.mean(pixel)
        if mean + cTRESHOLD < pixel[0]:
            im.putpixel(location, (255, 0, 0))
        elif mean + cTRESHOLD < pixel[1]:
            im.putpixel(location, (0, 255, 0))
        elif mean + cTRESHOLD < pixel[2]:
            im.putpixel(location, (0, 0, 255))
        elif mean < 100:
            im.putpixel(location, (255, 255, 255))
        else:
            im.putpixel(location, (0, 0, 0))
        


im.save("./reversed_2.PNG")