from PIL import Image

im_red = Image.open("./MoSe2BNMoSe2/red.png").convert("RGB").split()[0]

im_green = Image.open("./MoSe2BNMoSe2/green.png").convert("RGB").split()[1]

im_blue = Image.open("./MoSe2BNMoSe2/blue.png").convert("RGB").split()[2]

source = (im_red, im_green, im_blue)

im = Image.merge("RGB", source)

im.show()

im.save("./MoSe2BNMoSe2/combined.PNG")