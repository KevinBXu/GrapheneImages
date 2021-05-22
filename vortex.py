from PIL import Image
from orderedset import OrderedSet


im = Image.open ("combined.png")

[xs, ys] = im.size

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

def edge(location):
    x = max(0, min(xs - 1, location[0]))
    y = max(0, min(ys - 1, location[1]))
    return (x, y)

def vortices(point, vortex, antivortex):
    boundary = 10
    order = OrderedSet()
    for i in range (-boundary, boundary):
        location = edge((point[0]+i, point[1]-boundary))
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]+boundary, point[1]+i))
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]-i, point[1]+boundary))
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]-boundary, point[1]-i))
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    return order

def identify(pointlist, linelist):
    found = False
    isNode = False
    for pixel in pointlist:
        for line in linelist:
            if found:
                break
            for point in line:
                if distance(pixel, point) < 5:
                    for node in avg:
                        if distance(pixel, node) < 5:
                            line.append(node)
                            isNode = True
                            break
                    if not isNode:
                        line.append(pixel)
                    else:
                        isNode = False
                    found = True
                    break
        if found:
            found = False
        else:
            pointlist.append([pixel])


def find_vortexes(avg):

    vortex = []
    antivortex = []

    nodes = []

    for node_dict in avg:
        tmp = {}
        node = node_dict["coord"]
        tmp["coord"] = node
        if node in [(404, 107)]:
            tmp["vertex"] = True
        elif vortices(node, vortex, antivortex) in [OrderedSet([(0, 0, 255), (255, 0, 0), (0, 255, 0)]), OrderedSet([(255, 0, 0), (0, 255, 0), (0, 0, 255)]), OrderedSet([(0, 255, 0), (0, 0, 255), (255, 0, 0)])]:
            tmp["vertex"] = True
        else:
            tmp["vertex"] = False
        tmp["lines"] = []
        tmp["group"] = node_dict["group"]
        nodes.append(tmp)
    return nodes