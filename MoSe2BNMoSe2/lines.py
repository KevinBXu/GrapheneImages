import matplotlib.pyplot as plt
from vortex import find_vortexes
from csaps import csaps
import scipy as scipy
import numpy as np
from helper import distance, add, div, print_lines, create_mesh, print_lines_window, euclidean, sort_line
import cv2 as cv

image_name = "combined.png"
output = "Moire_MoSe"
node_radius = 2     #radius of circle to remove around the nodes
node_search_radius = 5      #search radius to assign nodes to segments
spline_smoothness = 0.9999  #smoothness of the fitting spline
cLC = 10.0      #mesh density

def main():

    im = cv.imread(image_name)

    b, g, r = cv.split(im)

    im_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    ret, im_bw = cv.threshold(im_gray, 254, 255, cv.THRESH_BINARY)
    #cv.imshow('Dilated Image', im_gray)
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

    nodelist, avg = [], []

    #find the nodes
    n, labels = cv.connectedComponents(im_bw)
    nodelist = [[] for x in range(n - 1)]
    for idx, x in np.ndenumerate(labels):
        if x != 0:
            nodelist[x - 1].append(idx)
                    
    #average together the nodes
    for group in nodelist:
        total = (0,0)
        for point in group:
            total = add(total, point)
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
    for node in [node for group in nodelist for node in group]:
        radius = 20
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                x = min(xs - 1, max(0, node[0] + i))
                y = min(ys - 1, max(0, node[1] + j))
                if euclidean((x, y), node) <= node_radius:
                    r[x, y] = 0
                    g[x, y] = 0
                    b[x, y] = 0

    #cv.imshow('Dilated Image', r + g + b)
    #cv.waitKey(0) 
    
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
                if euclidean(node["coord"], point) < node_search_radius:
                    segment["endpoints"].append(node)
                    break
        for line in lines:
            if segment["points"][0] in line["coord"] and segment["color"] == line["color"]:
                segment["line"] = line
                break

    #print_lines([segment["points"] for segment in segments if segment["color"] == "blue"] + [[node["coord"] for node in segment["endpoints"]] for segment in segments])
    
    #print_lines([line["coord"] for line in lines])
    #print_lines([segment["points"] for segment in segments])
    

    #label the segments with values and colors
    numbers = [0, 1, 0, 0, -5, -4, -3, -3, -2, -2, -1, -1, 0, 1, 5, 4, 4, 3, 2, 1, 1, 1, 0, 0, -1, 0]
    for line in lines:
        #print(line["color"])
        #print_lines_window([[(point[1], xs - point[0]) for point in line["coord"]]], ys, xs)
        line["value"] = numbers.pop(0)

    """
    for node in nodes:
        print([line["value"] for line in node["lines"] if "value" in line])

    for color in ["red", "green", "blue"]:
        temp = sorted([line for line in lines if line["color"] == color], key = lambda x : x["value"])
        for line in temp:
            print(line["color"] + str(line["value"]))
            print_lines_window([line["coord"]], xs, ys)
    """

    #for segment in segments:
        #print_lines_window([[(point[1], ys - point[0]) for point in segment["points"]], [(node["coord"][1], ys - node["coord"][0]) for node in segment["endpoints"]] + [(0, 0)]], xs, ys)

    delete = []
    #determine the knots of the spline
    for segment in segments:
        if "value" not in segment["line"]:
            delete.append(segment)
            continue
        segment["value"] = segment["line"]["value"]
        
        # fit the splines
        all_points = segment["points"].copy()
        for endpt in segment["endpoints"]:
            all_points.append(endpt["coord"])
        
        if len(segment["endpoints"]) != 0:
            endpoint = segment["endpoints"][0]["coord"]
            tmp = sorted(all_points, key = lambda x : (endpoint[0] - x[0]) ** 2 + (endpoint[1] - x[1]) ** 2)
        else:
            tmp = sort_line(all_points)


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
        np.put(weight, endpoint_indexes, 100000000)

        data_i = csaps(x, y, theta_i, smooth=spline_smoothness, weights=weight)
        xi = data_i[0, :]
        yi = data_i[1, :]

        parameter = x = np.linspace(0, 1, (len(xi)))
        tck, u = scipy.interpolate.splprep([xi, yi], u=parameter, s=0.01)

        knots = scipy.interpolate.splev(tck[0], tck)
        snd_spline = scipy.interpolate.splev(u, tck)

        #plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x')
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
        
        
        plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x', xi, yi, "-", [y[0][i] for i in endpoint_indexes], [y[1][i] for i in endpoint_indexes], "ro")
        #plt.plot(y[0], y[1], '.', [knot[0] for knot in segment["knots"]], [knot[1] for knot in segment["knots"]], 'x', xi, yi, "-", snd_spline[0], snd_spline[1], "-")
        #plt.show()
    ax = plt.gca() #you first need to get the axis handle
    ax.set_aspect(1) #sets the height to width ratio to 1.5. 
    plt.xlim([0, xs])
    plt.ylim([0, ys])
    plt.show() 

    for segment in delete:
        segments.remove(segment)

    #create the mesh
    mesh_points = set()
    for segment in segments:
        mesh_points = mesh_points.union(set(segment["knots"]))

    create_mesh(segments, lines, mesh_points, ys, xs, output, cLC)

    r_values = [segment["value"] for segment in segments if segment["color"] == "red"]
    g_values = [segment["value"] for segment in segments if segment["color"] == "green"]
    b_values = [segment["value"] for segment in segments if segment["color"] == "blue"]

    print(min(r_values))
    print(max(r_values))
    print(min(g_values))
    print(max(g_values))
    print(min(b_values))
    print(max(b_values))



if __name__ == "__main__":
    main()
