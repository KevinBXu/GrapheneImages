from PIL import Image
import matplotlib.pyplot as plt
from orderedset import OrderedSet

def convert(i):
    if i > 5:
        return 255
    else:
        return i

def distance(p1, p2):
    x = abs(p1[0]-p2[0])
    y = abs(p1[1]-p2[1])
    return max(x,y)

def sum(p1, p2):
    x = p1[0]+p2[0]
    y = p1[1]+p2[1]
    return (x,y)

def div(p, c):
    x = round(p[0] / c)
    y = round(p[1] / c)
    return (x,y)

def edge(point, color):
    surround = 0
    boundary = 2
    for i in [-boundary,-boundary+1,0,boundary-1,boundary]:
        for j in [-boundary,0,boundary]:
            x = max(0, min(xs-1, point[0]+i))
            y = max(0, min(ys-1, point[1]+j))
            if im.getpixel((x,y)) == color:
                surround += 1
            if im.getpixel((x,y)) not in [color, (0, 0 , 0)]:
                surround += 1
    if surround > 13:
        return True
    else:
        return False


im_red = Image.open("./trim_red.png")

source = im_red.split()

out_red = source[0].point(convert)

im_green = Image.open("./trim_green.png")

source = im_green.split()

out_green = source[1].point(convert)

im_blue = Image.open("./trim_blue.png")

source = im_blue.split()

out_blue = source[2].point(convert)

source = (out_red, out_green, out_blue)

im = Image.merge("RGB", source)

im.show()

#im.save("./combined.PNG")

[xs, ys] = im.size

redlist = []

greenlist = []

bluelist = []

nodelist = []

avg = []

found = False

red = (255, 0, 0)

green = (0, 255, 0)

blue = (0, 0, 255)

white = (255, 255, 255)


for i in range(xs):
    for j in range (ys):
        location = (i,j)
        pixel = im.getpixel(location)
        if pixel == red:
            redlist.append(location)
        elif pixel == green:
            greenlist.append(location)
        elif pixel == blue:
            bluelist.append(location)
        elif pixel == white:
            nodelist.append(location)

#plt.scatter(*zip(*(redlist+greenlist+bluelist+avg)), s=0.25)
#plt.show()

redlines = []
greenlines = []
bluelines = []

        

#print(redlist)

#print(bluelist)

#print(greenlist)

print(nodelist)
print(len(nodelist))



