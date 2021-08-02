import matplotlib.pyplot as plt
from vortex import find_vortexes
from csaps import csaps
import scipy as scipy
import numpy as np
from helper import distance, add, div, print_lines, create_mesh, print_lines_window, euclidean, sort_line
import cv2 as cv

image_name = "./ArtificialBubbles/iso_21_-y.png"
output = "ArtificialBubbles/Moire_iso_21_-y"
dilation = 3        #radius of the dilation
node_radius = 1     #radius of circle to remove around the nodes
node_search_radius = 30     #search radius to assign nodes to segments
spline_smoothness = 0.9999  #smoothness of the fitting spline
cLC = 10.0      #mesh density

def main():
    im = cv.imread(image_name)

    #split im into RGB channels (aka red, green, blue lines)
    b, g, r = cv.split(im)

    #create an image with only the white pixels
    im_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    ret, im_bw = cv.threshold(im_gray, 254, 255, cv.THRESH_BINARY)

    #dilate the nodes to ensure that they are not segmented
    kernel = np.ones((dilation, dilation), 'uint8')
    im_bw = cv.dilate(im_bw, kernel, iterations=2)

    cv.imshow('Dilated Image', im_bw)
    cv.waitKey(0) 

    #use connectedComponents to identify the lines in each channel
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

    #find the node pixels
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

    print_lines(redlines + greenlines + bluelines + nodelist)

    #find the vortices - deprecated
    nodes = find_vortexes(avg, image_name)

    #sort the nodes based on distance to the origin
    nodes.sort(key = lambda x : euclidean(x["coord"], (xs, ys)))

    #create a list of dictionaries to represent the lines
    #color - color of the line
    #coord - coordinates of the points that make up the line
    #nodes - node dictionaries that are in the line
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

    #in each channel, remove any pixel that is around a node
    #separates each line in each channel into segments
    for node in [node for group in nodelist for node in group]:
        radius = node_radius
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                x = min(xs - 1, max(0, node[0] + i))
                y = min(ys - 1, max(0, node[1] + j))
                #remove the pixels in within node_radius of any node pixel
                if euclidean((x, y), node) <= node_radius:
                    r[x, y] = 0
                    g[x, y] = 0
                    b[x, y] = 0

    cv.imshow('Dilated Image', r + g + b)
    cv.waitKey(0) 
    
    #identify the segments in each channel and create a dictionary for each
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
    #append any node that is the endpoint of a segment
    #identify which line is the parent of the segment
    #points - coordinates of the points in the segment
    #color - color of the segment
    #line - parent line of the segment
    #endpoints - nodes which lie at the endpoints of the segment
    for segment in segments:
        segment["endpoints"] = []
        sorted_seg = sort_line(segment["points"])
        for node in nodes:
            for point in [sorted_seg[0], sorted_seg[-1]]:
                if euclidean(node["coord"], point) <= node_search_radius:
                    segment["endpoints"].append(node)
                    break
        """
        if len(segment["endpoints"]) != 2:
            for node in [node for node in nodes if node not in segment["endpoints"]]:
                for point in sorted_seg:
                    if euclidean(node["coord"], point) <= node_search_radius:
                        segment["endpoints"].append(node)
                        break
        """
        #delete segments that do not have any node endpoints
        #ensures that the numbering algorithm functions correctly
        if len(segment["endpoints"]) == 0:
            print('test')
            delete.append(segment)
            continue
        for line in lines:
            if segment["points"][0] in line["coord"] and segment["color"] == line["color"]:
                segment["line"] = line
                break

    for segment in delete:
        segments.remove(segment)
    #also remove any lines that do not have nodes
    for line in lines:
        if len(line["nodes"]) == 0:
            lines.remove(line)

    #print_lines([segment["points"] for segment in segments if segment["color"] == "blue"] + [[node["coord"] for node in segment["endpoints"]] for segment in segments])
    #print_lines([line["coord"] for line in lines])
    print_lines([segment["points"] for segment in segments])
    

    #label the segments with values and colors
    nodes.sort(key = lambda x : euclidean((xs / 2, ys / 2), x["coord"]))
    first = nodes[0]
    print_lines_window([[first["coord"]]] + [segment["points"] for segment in segments if first in segment["endpoints"]], xs, ys)
    #label the origin node (r, g, b) = (0, 0, 0)
    for line in first["lines"]:
        line["value"] = 0
    pending = [first]
    visited = []

    #find a neighboring node
    for segment in segments:
        if first in segment["endpoints"] and segment["color"] == "red":
            for endpoint in segment["endpoints"]:
                if endpoint is not first:
                    second = endpoint
            break
    
    #label the second node with (0, 1, -1)
    #note: once two nodes are labeled, the direction (chirality) has been chosen
    init = 1
    for line in second["lines"]:
        if "value" not in line:
            line["value"] = init
            init = -1

    #track the numbered nodes
    computed = [first, second]
    
    #bf search through the rest of the nodes
    while pending != []:
        search = pending.pop(0)
        if search in visited:
            continue 
        visited.append(search)

        connecting = [segment for segment in segments if search in segment["endpoints"] and len(segment["endpoints"]) == 2]
        neighbors = [endpoint for segment in connecting for endpoint in segment["endpoints"] if endpoint is not search and endpoint not in computed]
        pending = pending + [neighbor for neighbor in neighbors if neighbor not in pending]

        #number every node surrounding search
        #note: uses the property that r+g+b=0 for any node
        #can run a maximum of n^2 times
        count = 0
        while neighbors != [] and count < 64:
            neighbor = neighbors.pop(0)
            known_lines = [line for line in neighbor["lines"] if "value" in line]
            values = [line["value"] for line in known_lines]
            if len(known_lines) == 3:
                computed.append(neighbor)
            elif len(known_lines) == 2:
                unknown_line = [line for line in neighbor["lines"] if "value" not in line][0]
                unknown_line["value"] = -sum(values)
                computed.append(neighbor)
            elif len(known_lines) == 1:
                neighbors.append(neighbor)
            #edge case in which a node is completely isolated
            #elif len(known_lines) == 0:
                #raise Exception("Not enough lines known")
            count += 1


    #sort the segments by length
    segments.sort(key = lambda x : len(x["points"]), reverse = False)
    
    """
    delete = []
    for line in lines:
        if "value" not in line:
            delete.append(line)
    for line in delete:
        lines.remove(line)
    """

    #remove the small segments that intersect
    """
    delete = []
    for segment in segments:
        if len(segment["endpoints"]) == 1 and len(segment["points"]) < 1000:
            delete.append(segment)
    for segment in delete:
        segments.remove(segment)
    """

    """
    for node in nodes:
        print([line["value"] for line in node["lines"] if "value" in line])

    for color in ["red", "green", "blue"]:
        temp = sorted([line for line in lines if line["color"] == color], key = lambda x : x["value"])
        for line in temp:
            print(line["color"] + str(line["value"]))
            print_lines_window([line["coord"]], xs, ys)
    """
    
    delete = []
    #determine the knots of the spline
    for segment in segments:
        #remove the segments that could not be numbered
        if "value" not in segment["line"]:
            delete.append(segment)
            continue
        segment["value"] = segment["line"]["value"]
        
        #sort the segment from endpoint to endpoint
        endpoint = segment["endpoints"][0]["coord"]
        all_points = segment["points"].copy()
        for endpt in segment["endpoints"]:
            all_points.append(endpt["coord"])
        tmp = sorted(all_points, key = lambda x : (endpoint[0] - x[0]) ** 2 + (endpoint[1] - x[1]) ** 2)

        endpoint_indexes = []
        for endpt in segment["endpoints"]:
            endpoint_indexes.append(tmp.index(endpt["coord"]))

        #change the data to fit the spline library
        y = [(), ()]
        x = np.linspace(0, 1, (len(tmp)))
        for point in tmp:
            y[0] = y[0] + (point[0],)
            y[1] = y[1]+ (point[1],)

        theta_i = np.linspace(0, 1, 200)
        #weight the spline so that it passes through the endpoints
        weight = np.ones_like(x)
        np.put(weight, endpoint_indexes, 100000000)

        data_i = csaps(x, y, theta_i, smooth=0.99, weights=weight)
        xi = data_i[0, :]
        yi = data_i[1, :]

        parameter = x = np.linspace(0, 1, (len(xi)))
        tck, u = scipy.interpolate.splprep([xi, yi], u=parameter, s=0.01)

        knots = scipy.interpolate.splev(tck[0], tck)
        snd_spline = scipy.interpolate.splev(u, tck)

        #plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x')
        #plt.show()

        knot_points = []

        #ensure that the endpoints are a knot on the spline
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
        
        
        #plt.plot(y[0], y[1], '.', knots[0], knots[1], 'x', xi, yi, "-", [y[0][i] for i in endpoint_indexes], [y[1][i] for i in endpoint_indexes])
        plt.plot(y[0], y[1], '.', [knot[0] for knot in segment["knots"]], [knot[1] for knot in segment["knots"]], 'x', xi, yi, "-", snd_spline[0], snd_spline[1], "-")
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

    #print the min and max values for each color to use in the strain calculation
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
