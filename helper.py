import gmsh
import matplotlib.pyplot as plt
import math

cLINE_TRESHOLD = 300
cRADIUS = 10
cCHECK_POINTS = 100

#find the distance between two (x, y) coordinates using the max metric
def distance(p1, p2):
    x = abs(p1[0]-p2[0])
    y = abs(p1[1]-p2[1])
    return max(x,y)

def euclidean(p1, p2):
    return (math.sqrt((p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2))

#add two cartesian coordinates
def sum(p1, p2):
    x = p1[0]+p2[0]
    y = p1[1]+p2[1]
    return (x,y)

#divide a cartesian coordinate by a scalar
def div(p, c):
    x = round(p[0] / c)
    y = round(p[1] / c)
    return (x,y)

#print the lines using pyplot
def print_lines(l):
    for line in l:
        plt.scatter(*zip(*(line)), s=0.25)
    plt.show()

#overloaded function
def print_lines_window(l, xs, ys):
    for line in l:
        plt.scatter(*zip(*(line)), s=0.25)
    plt.xlim([0, xs])
    plt.ylim([0, ys])
    plt.show()

#create the mesh
def create_mesh(segments, lines, points, xs, ys, mesh_name):
    point_dict = {}
    count = -1
    for point in points:
        point_dict[point] = (count := count + 1) 


    cLC = 10.

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("Moire")

    boundary_points = [(0, 0), (0, ys), (xs, ys), (xs, 0)]

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

    print(boundary)

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

    for line in lines:
        if "value" not in line:
            continue
        spline_tags = []
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
    gmsh.write("./MoireImages/" + mesh_name + ".msh")
    gmsh.write("./MoireImages/" + mesh_name + ".vtk")
    gmsh.finalize()