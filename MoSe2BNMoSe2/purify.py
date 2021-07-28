from PIL import Image

def convert(i):
    if i > 0:
        return 255
    else:
        return 0

[r, g, b] = Image.open("./combined.png").convert("RGB").split()

im_red = r.point(convert)

im_green = g.point(convert)

im_blue = b.point(convert)

source = (im_red, im_green, im_blue)

im = Image.merge("RGB", source)

im.show()

im.save("./purified.PNG")