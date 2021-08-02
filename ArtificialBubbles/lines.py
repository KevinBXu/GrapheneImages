from PIL import Image
import matplotlib.pyplot as plt
from vortex import find_vortexes
import itertools
from csaps import csaps
import scipy as scipy
import numpy as np
from helper import distance, sum, div, find_line, find_line_more, create_lines, create_lines_check_all, print_lines, create_mesh, fix_lines, swap, print_lines_window
import cv2 as cv 


image_name = "iso_background_inverted.png"
output = "iso"

def main():

    im = cv.imread(image_name)

    kernel = np.ones((5, 5), 'uint8')

    im = cv.dilate(im, kernel, iterations=1)
    #cv.imshow('Dilated Image', im)
    #cv.waitKey(0) 

    b, g, r = cv.split(im)

    im_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    ret, im_bw = cv.threshold(im_gray, 254, 255, cv.THRESH_BINARY)

    kernel = np.ones((3, 3), 'uint8')
    im_bw = cv.dilate(im_bw, kernel, iterations=1)
    #cv.imshow('Dilated Image', im_bw)
    #cv.waitKey(0) 

    redlines, bluelines, greenlines = [], [], []
    for image in [r, g, b]:
        n, labels = cv.connectedComponents(image)

        if image is r:
            redlines = [[] for x in range(n - 1)]
            line = redlines
        elif image is g:
            greenlines = [[] for x in range(n - 1)]
            line = greenlines
        elif image is b:
            bluelines = [[] for x in range(n - 1)]
            line = bluelines

        for idx, x in np.ndenumerate(labels):
            if x != 0:
                line[x - 1].append(idx)


    [xs, ys] = im.shape[:2]

    #find the nodes
    n, labels = cv.connectedComponents(im_bw)
    nodelist = [[] for x in range(n - 1)]
    for idx, x in np.ndenumerate(labels):
        if x != 0:
            nodelist[x - 1].append(idx)
                    
    #average together the nodes
    avg = []
    for group in nodelist:
        total = (0,0)
        for point in group:
            total = sum(total, point)
        tmp = {}
        tmp["coord"] = div(total, len(group))
        tmp["group"] = group
        avg.append(tmp)

    #print_lines(redlines + greenlines + bluelines + nodelist)

    #find the vortices
    nodes = find_vortexes(avg, image_name)

    nodes.sort(key = lambda x : (xs - x["coord"][0]) ** 2 + (ys - x["coord"][1]) ** 2)

    #create the dictionaries for the lines and label the colors
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
        line_dict["node_coords"] = []
        for node in nodes:
            if node["coord"] in line:
                line_dict["nodes"].append(node)
                line_dict["node_coords"].append(node["coord"])
                node["lines"].append(line_dict)
        lines.append(line_dict)

    #remove the nodes from the images
    for node in nodelist:
        for point in node:
            r[point[0], point[1]] = 0
            g[point[0], point[1]] = 0
            b[point[0], point[1]] = 0

    #separate the segments
    segments = []
        
    for image in [r, g, b]:
        n, labels = cv.connectedComponents(image)
        if image is r:
            color = "red"
        if image is g:
            color = "green"
        if image is b:
            color = "blue"

        segment = [{"points" : [], "color" : color} for x in range(n - 1)]
        for idx, x in np.ndenumerate(labels):
            if x != 0:
                segment[x - 1]["points"].append(idx)
        segments += segment

    delete = []
    for segment in segments:
        segment["endpoints"] = []
        for node in nodes:
            for point in segment["points"]:
                if distance(node["coord"], point) < 20:
                    segment["endpoints"].append(node)
                    break
        if len(segment["endpoints"]) == 0:
            delete.append(segment)
            continue
        for line in lines:
            if segment["endpoints"][0] in line["nodes"] and segment["color"] == line["color"]:
                segment["line"] = line
                break

    #clean the segments and the lines
    for segment in delete:
        segments.remove(segment)
    for line in lines:
        if len(line["nodes"]) == 0:
            lines.remove(line)

    #print_lines([[node["coord"] for node in segment["endpoints"]] for segment in segments])
    #print_lines([line["coord"] for line in lines])

    #label the segments with values and colors
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
                        if neighbor["coord"][0] > search["coord"][0]:
                            change = 1
                        else:
                            change = -1
                        for line in other_lines:        
                            if "value" not in line:
                                if line["color"] == "green":
                                    line["value"] = green - change
                                elif line["color"] == "blue":
                                    line["value"] = blue + change
                    elif segment["color"] == "green":
                        if neighbor["coord"][1] > search["coord"][1]:
                            change = 1
                        else:
                            change = -1
                        for line in other_lines:        
                            if "value" not in line:
                                if line["color"] == "red":
                                    line["value"] = red - change
                                elif line["color"] == "blue":
                                    line["value"] = blue + change

                pending.append(neighbor)
        visited.append(search)
        
    """
    for segment in lines:
        print_lines_window([segment["coord"]], xs, ys)
        print(segment["color"] + str(segment["value"]))
    """

    for node in nodes:
        print([line["value"] for line in node["lines"]])
  
    #clean the segments
    segments.sort(key = lambda x : len(x["points"]), reverse = True)
    """
    for segment in segments:
        if len(segment["endpoints"]) == 1:
            segments.remove(segment)
    """

    #determine the knots
    for segment in segments:
        segment["value"] = segment["line"]["value"]
        
        # fit the splines
        endpoint = segment["endpoints"][0]["coord"]
        all_points = segment["points"].copy()
        for endpt in segment["endpoints"]:
            all_points.append(endpt["coord"])
            #all_points += endpt["group"]

        tmp = sorted(all_points, key = lambda x : (endpoint[0] - x[0]) ** 2 + (endpoint[1] - x[1]) ** 2)

        endpoint_indexes = []

        for endpt in segment["endpoints"]:
            endpoint_indexes.append(tmp.index(endpt["coord"]))

        y = [(), ()]
        x = np.linspace(0, 1, (len(tmp)))
        for point in tmp:
            y[0] = y[0] + (point[0],)
            y[1] = y[1]+ (point[1],)

        theta_i = np.linspace(0, 1, 200)
        weight = np.ones_like(x)
        np.put(weight, endpoint_indexes, 1000000)

        data_i = csaps(x, y, theta_i, smooth=0.9, weights=weight)
        xi = data_i[0, :]
        yi = data_i[1, :]

        """
        for i in range(len(segment["endpoints"])):
            endpt = segment["endpoints"][i]
            if i == 0:
                xi = np.insert(xi, 0, [endpt["coord"][0]])
                yi = np.insert(yi, 0, [endpt["coord"][1]])
            else:
                xi = np.append(xi, [endpt["coord"][0]])
                yi = np.append(yi, [endpt["coord"][1]])
        """

        #plt.plot(xi, yi, "-", y[0], y[1], '.')

        #plt.show()

        parameter = x = np.linspace(0, 1, (len(xi)))
        tck, u = scipy.interpolate.splprep([xi, yi], u=parameter, s=0.01)

        knots = scipy.interpolate.splev(tck[0], tck)
        snd_spline = scipy.interpolate.splev(u, tck)

        #plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x', xi, yi, "-", [y[0][i] for i in endpoint_indexes], [y[1][i] for i in endpoint_indexes])

        #plt.show()

        knot_points = []

        for i in range(len(tck[0])):
            point = (knots[0][i], knots[1][i])
            """
            redundant = False
            for knot_point in knot_points:
                if distance(point, knot_point) < 2:
                    redundant = True
            if not redundant:
            """
            for endpt in segment["endpoints"]:
                if distance(endpt["coord"], point) < 1:
                    break
            else:
                knot_points.append(point)

        for endpt in segment["endpoints"]:
            if endpt is segment["endpoints"][0]:
                knot_points.insert(0, endpt["coord"])
            else:
                knot_points.append(endpt["coord"])

        segment["knots"] = knot_points

        plt.plot(y[0], y[1], '.', [knot[0] for knot in segment["knots"]], [knot[1] for knot in segment["knots"]], 'x', xi, yi, "-", snd_spline[0], snd_spline[1], "-")
        #print_lines([knot_points] + [tmp])
    plt.show()
    #print_lines_window([segment["knots"] for segment in segments], xs, ys)
     
    #create the mesh
    mesh_points = []

    for segment in segments:
        for point in segment["knots"]:
            if point not in mesh_points:
                mesh_points.append(point)

    r_values = [segment["value"] for segment in segments if segment["color"] == "red"]
    g_values = [segment["value"] for segment in segments if segment["color"] == "green"]
    b_values = [segment["value"] for segment in segments if segment["color"] == "blue"]

    print(min(r_values))
    print(max(r_values))
    print(min(g_values))
    print(max(g_values))
    print(min(b_values))
    print(max(b_values))

    create_mesh(segments, lines, mesh_points, ys, xs, output)



if __name__ == "__main__":
    main()
