import gmsh
import matplotlib.pyplot as plt
import math

#find the distance between two (x, y) coordinates using the max metric
def distance(p1, p2):
    x = abs(p1[0]-p2[0])
    y = abs(p1[1]-p2[1])
    return max(x,y)

#find the distance between two (x, y) coordinates using the euclidean metric
def euclidean(p1, p2):
    return (math.sqrt((p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2))

#add two cartesian coordinates
def add(p1, p2):
    x = p1[0]+p2[0]
    y = p1[1]+p2[1]
    return (x,y)

#divide a cartesian coordinate by a scalar
def div(p, c):
    x = round(p[0] / c)
    y = round(p[1] / c)
    return (x,y)

#print the lines using pyplot
# l - list containing lists of points (lines)
def print_lines(l):
    for line in l:
        plt.scatter(*zip(*(line)), s=0.25)
    plt.show()

#functions similarly to print_lines but uses xs, ys for the axes
def print_lines_window(l, xs, ys):
    for line in l:
        plt.scatter(*zip(*(line)), s=0.25)
    plt.xlim([0, xs])
    plt.ylim([0, ys])
    plt.show()

#return the points above, below, left, and right of p
def get_circle(p):
    return [(p[0] - 1, p[1]), (p[0] + 1, p[1]), (p[0], p[1] - 1), (p[0], p[1] + 1)]

#returns segment sorted from one endpoint to the other
def sort_line(segment):
    #determines one endpoint by using breadth first search starting from an arbitrary point
    check = [segment[0]]
    visited = check[:]

    while len(check) != 0:
        for point in get_circle(check.pop(0)):
            if point in segment and point not in visited:
                visited.append(point)
                check.append(point)

    #the point visited last should be an endpoint
    endpoint = visited.pop()

    #visits every point starting from the endpoint using bf search
    #the resulting list has the points in order from one endpoint to the other
    check = [endpoint]
    visited = check[:]

    while len(check) != 0:
        for point in get_circle(check.pop(0)):
            if point in segment and point not in visited:
                visited.append(point)
                check.append(point)

    return visited

#create the mesh
#segments - list of the segments (as dictionaries)
#lines - list of the lines 
#points - list of all knots and nodes
#xs, ys - dimensions of the image
#mesh_name - name of the resulting file
#cLC - size of the generated mesh triangles
def create_mesh(segments, lines, points, xs, ys, mesh_name, cLC):
    #map each point in points to an index
    point_dict = {}
    count = -1
    for point in points:
        point_dict[point] = (count := count + 1) 

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("Moire")

    #generate the boundary of the mesh
    boundary_points = [(-10, -10), (-10, ys + 10), (xs + 10, ys + 10), (xs + 10, -10)]
    for key in point_dict:
        gmsh.model.geo.addPoint(key[1], ys - key[0], 0, cLC, point_dict[key])

    boundary = []
    loop = 0
    for i in range(len(boundary_points)):
        if i == 0:
            loop = gmsh.model.geo.addPoint(boundary_points[i][0], boundary_points[i][1], 0, cLC)
            boundary.append(loop)
        else:
            boundary.append(gmsh.model.geo.addPoint(boundary_points[i][0], boundary_points[i][1], 0, cLC))
    boundary.append(loop)

    tags = [None] * (len(boundary) - 1)
    for i in range(len(boundary) - 1):
        tags[i] = gmsh.model.geo.addLine(boundary[i], boundary[i+1])

    btag = gmsh.model.geo.addCurveLoop(tags, len(boundary))
    dtag = gmsh.model.geo.addPlaneSurface([btag])
    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(1, tags, 1)
    gmsh.model.setPhysicalName(1, 1, "boundary")
    gmsh.model.addPhysicalGroup(2, [dtag], 1)
    gmsh.model.setPhysicalName(2, 1, "domain")

    #add the lines to the image
    for line in lines:
        if "value" not in line:
            continue
        spline_tags = []
        #splines cannot cross so segments have to be added individually
        for segment in segments:
            if segment["line"] != line:
                continue
            knot_indexes = []
            for point in segment["knots"]:
                knot_indexes.append(point_dict[point])
            spline_tags.append(gmsh.model.geo.addBSpline(knot_indexes))
        gmsh.model.geo.synchronize()
        ltag = gmsh.model.addPhysicalGroup(1, spline_tags)
        gmsh.model.setPhysicalName(1, ltag, line["color"] + " " + str(line["value"]))
        gmsh.model.mesh.embed(1, spline_tags, 2, dtag)


    gmsh.model.mesh.setAlgorithm(2, dtag, 1)
    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.optimize("")
    gmsh.write(mesh_name + ".msh")
    gmsh.write(mesh_name + ".vtk")
    gmsh.finalize()