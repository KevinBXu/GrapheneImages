from PIL import Image

def convert(i):
    if i > 0:
        return 255
    else:
        return 0

im_red = Image.open("./Images/red.png").convert("RGB")

out_red = im_red.split()[0].point(convert)

im_green = Image.open("./Images/green.png").convert("RGB")

out_green = im_green.split()[1].point(convert)

im_blue = Image.open("./Images/blue.png").convert("RGB")

out_blue = im_blue.split()[2].point(convert)

source = (out_red, out_green, out_blue)

im = Image.merge("RGB", source)

im.show()

im.save("./combined.PNG")



