from PIL import Image

def convert(i):
    if i > 5:
        return 255
    else:
        return i

im_red = Image.open("./av_extend_red_left.png")

source = im_red.split()

out_red = source[0].point(convert)

im_green = Image.open("./av_extend_green_left.png")

source = im_green.split()

out_green = source[1].point(convert)

im_blue = Image.open("./av_extend_blue_left.png")

source = im_blue.split()

out_blue = source[2].point(convert)

source = (out_red, out_green, out_blue)

im = Image.merge("RGB", source)

im.show()

im.save("./combined.PNG")



