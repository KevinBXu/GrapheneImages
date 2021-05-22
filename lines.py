from PIL import Image
import matplotlib.pyplot as plt
from vortex import find_vortexes
import itertools
from csaps import csaps
import scipy as scipy
import numpy as np
from helper import distance, sum, div, find_line, find_line_more, create_lines, create_lines_check_all, print_lines, create_mesh, fix_lines


def main():
    im = Image.open ("combined.png")

    [xs, ys] = im.size

    redlist = []
    greenlist = []
    bluelist = []
    nodelist = []
    avg = []

    found = False

    white = (255, 255, 255)

    for i in range(xs):
        for j in range (ys):
            location = (i,j)
            pixel = im.getpixel(location)
            if pixel[0] == 255:
                redlist.append(location)
            if pixel[1] == 255:
                greenlist.append(location)
            if pixel[2] == 255:
                bluelist.append(location)
            if pixel == white:
                for group in nodelist:
                    if found:
                        break
                    for point in group:
                        if distance(point, location) < 5:
                            group.append(location)
                            found = True
                            break
                if found:
                    found = False
                else:
                    nodelist.append([location])
                    
    for group in nodelist:
        total = (0,0)
        for point in group:
            total = sum(total, point)
        tmp = {}
        tmp["coord"] = div(total, len(group))
        tmp["group"] = group
        avg.append(tmp)

    redlist.sort(key = lambda x : (x[1], x[0]))
    greenlist.sort(key = lambda x : (x[0], x[1]))
    bluelist.sort(key = lambda x : x[0] + x[1])

    redlines = create_lines(redlist)
    greenlines = create_lines(greenlist)
    bluelines = create_lines(bluelist)

    nodes = find_vortexes(avg)
    nodes.sort(key = lambda x : (xs - x["coord"][0]) ** 2 + (ys - x["coord"][1]) ** 2)

    lines = []
    for line in redlines + greenlines + bluelines:
        line_dict = {}
        if line in redlines:
            line_dict["color"] = "red"
        elif line in greenlines:
            line_dict["color"] = "green"
        else:
            line_dict["color"] = "blue"
        line_dict["coord"] = line
        line_dict["nodes"] = []
        for node in nodes:
            if node["coord"] in line:
                line_dict["nodes"].append(node)
                node["lines"].append(line_dict)
        lines.append(line_dict)

    segments = []
    for line in lines:
        points = line["coord"].copy()
        
        for node in line["nodes"]:
            point = node["coord"]
            for i in range(-7, 7):
                for j in range(-7, 7):
                    if (point[0] + i, point[1] + j) in points:
                        points.remove((point[0] + i, point[1] + j))
        
        for line_segment in create_lines_check_all(points):
            segment = {}
            segment["points"] = line_segment
            segment["endpoints"] = []
            segment["color"] = line["color"]
            segment["line"] = line

            visited = []
            count = 0
            for point, node in itertools.product(line_segment, line["nodes"]):
                coord = node["coord"]
                if node in visited:
                    continue
                if distance(point, coord) < 15:
                    segment["endpoints"].append(node)
                    visited.append(node)
                    if count == 0:
                        count += 1
                    else:
                        break
            segments.append(segment)


        return

    for segment in segments:
        if len(segment["points"]) < 300:
            fix_lines(segments, segment)

    """
    accum = []
    for segment in segments:
        if segment["color"] == "green":
            accum.append(segment["points"])
        for endpoint in segment["endpoints"]:
            accum.append([endpoint["coord"]])
    print_lines(accum)
    """

    nodes.sort(key = lambda x : (xs / 2 - x["coord"][0]) + (ys / 2 - x["coord"][1]))
    first = nodes[0]
    for line in first["lines"]:
        line["value"] = 0
    pending = [first]
    visited = []

    while True:
        if pending == []:
            break
        search = pending.pop(0)
        if search in visited:
            continue 

        red = 0
        green = 0 
        blue = 0
        for line in search["lines"]:
            if line["color"] == "red":
                red = line["value"]
            elif line["color"] == "green":
                green = line["value"]
            elif line["color"] == "blue":
                blue = line["value"]

        for segment in segments:
            if len(segment["endpoints"]) == 2 and search in segment["endpoints"] and segment["color"] != "blue":
                if segment["endpoints"][0] == search:
                    neighbor = segment["endpoints"][1]
                else:
                    neighbor = segment["endpoints"][0]

                other_lines = []
                for line in neighbor["lines"]:
                    if line["color"] != segment["color"]:
                        other_lines.append(line)

                change = 0
                if search["vertex"] and neighbor["vertex"]:
                    if segment["color"] == "red":
                        if neighbor["coord"][1] < search["coord"][1]:
                            change = 1
                        else:
                            change = -1
                    elif segment["color"] == "green":
                        if neighbor["coord"][0] > search["coord"][0]:
                            change = 1
                        else:
                            change = -1

                for line in other_lines:        
                    if "value" not in line:
                        if line["color"] == "red":
                            line["value"] = red + change
                        elif line["color"] == "green":
                            line["value"] = green + change
                        elif line["color"] == "blue":
                            line["value"] = blue + change
                pending.append(neighbor)
        visited.append(search)
        
    for i in range (-15, 15):
        for line in lines:
            if "value" in line:
                if line["value"] == i and line["color"] == "blue":
                    #print(line["value"])
                    tmp = line["coord"].copy()
                    tmp.append((xs, ys))
                    tmp.append((0, 0))
                    #print_lines([tmp])

    segments.sort(key = lambda x : len(x["points"]), reverse = True)
    for segment in segments:
        if len(segment["endpoints"]) == 0:
            segments.remove(segment)

    for segment in segments:

        segment["value"] = segment["line"]["value"]
        

        # fit the splines
        endpoint = segment["endpoints"][0]["coord"]
        all_points = segment["points"].copy()
        for endpt in segment["endpoints"]:
            all_points.append(endpt["coord"])
        tmp = sorted(all_points, key = lambda x : (endpoint[0] - x[0]) ** 2 + (endpoint[1] - x[1]) ** 2)
        y = [(), ()]
        x = np.linspace(0, 1, (len(tmp)))
        for point in tmp:
            y[0] = y[0] + (point[0],)
            y[1] = y[1]+ (point[1],)

        theta_i = np.linspace(0, 1, 200)
        data_i = csaps(x, y, theta_i, smooth=0.999)
        xi = data_i[0, :]
        yi = data_i[1, :]

        parameter = x = np.linspace(0, 1, (len(xi)))
        tck, u = scipy.interpolate.splprep([xi, yi], u=parameter, s=0.999)

        knots = scipy.interpolate.splev(tck[0], tck)

        #plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x')

        #plt.show()

        knot_points = []
        for i in range(len(tck[0])):
            point = (knots[0][i], knots[1][i])
            redundant = False
            for knot_point in knot_points:
                if distance(point, knot_point) < 2:
                    redundant = True
            if not redundant:
                knot_points.append(point)
        for endpt in segment["endpoints"]:
            knot_points.append(endpt["coord"])

        segment["knots"] = knot_points

    mesh_points = set()
    for segment in segments:
        mesh_points = mesh_points.union(set(segment["knots"]))

    create_mesh(segments, lines, mesh_points, xs, ys)



if __name__ == "__main__":
    main()
