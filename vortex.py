from PIL import Image
from orderedset import OrderedSet
from helper import distance


def edge(location, im):
    [xs, ys] = im.size

    x = max(0, min(xs - 1, location[0]))
    y = max(0, min(ys - 1, location[1]))
    return (x, y)

def vortices(point, im):

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    boundary = 10
    order = OrderedSet()
    for i in range (-boundary, boundary):
        location = edge((point[0]+i, point[1]-boundary), im)
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]+boundary, point[1]+i), im)
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]-i, point[1]+boundary), im)
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    for i in range (-boundary, boundary):
        location = edge((point[0]-boundary, point[1]-i), im)
        if im.getpixel(location) in [red, green, blue]:
            order.add(im.getpixel(location))
    return order


def find_vortexes(avg, image):

    im = Image.open(image)

    nodes = []

    for node_dict in avg:
        tmp = {}
        node = node_dict["coord"]
        tmp["coord"] = node
        if vortices(node, im) in [OrderedSet([(0, 0, 255), (255, 0, 0), (0, 255, 0)]), OrderedSet([(255, 0, 0), (0, 255, 0), (0, 0, 255)]), OrderedSet([(0, 255, 0), (0, 0, 255), (255, 0, 0)])]:
            tmp["vertex"] = False
        else:
            tmp["vertex"] = True
        tmp["lines"] = []
        tmp["group"] = node_dict["group"]
        nodes.append(tmp)
    return nodes