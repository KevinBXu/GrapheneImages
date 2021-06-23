import gmsh
import matplotlib.pyplot as plt

cLINE_TRESHOLD = 300
cRADIUS = 10
cCHECK_POINTS = 100

#swap the cartesian coordinate
def swap(p):
    return (p[1], p[0])

#find the distance between two (x, y) coordinates using the max metric
def distance(p1, p2):
    x = abs(p1[0]-p2[0])
    y = abs(p1[1]-p2[1])
    return max(x,y)

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

#find the points that belong to a line
def find_line(point, lines, radius):
    for line in lines:
        if distance(point, line[len(line) - 1]) < radius:
            line.append(point)
            return True
    return False

#find the points that belong to a line, except it checks num amount of points in the line
def find_line_more(point, lines, num, radius):
    for i in range(1, num):
        for line in lines:
            index = len(line) - i 
            if index < 0:
                continue
            if distance(point, line[index]) < radius:
                line.append(point)
                return
    lines.append([point])
    return

#returns a list of lines
#runs find_line_more if find_line fails to assign a point to a line
def create_lines(lists):
    lines = []
    lines.append([lists[0]])
    for i in range(1, len(lists)):
        point = lists[i]
        if not find_line(point, lines, cRADIUS):
            if i <= cLINE_TRESHOLD:
                lines.append([point])
            else: 
                find_line_more(point, lines, cCHECK_POINTS, cRADIUS)
    return lines

#returns a list of lines
#runs find_line_more no matter what
def create_lines_check_all(lists):
    lines = []
    start = lists[0]
    lines.append([start])
    tmp = lists.copy()
    tmp.sort(key = lambda x : abs(start[0] - x[0]) + abs(start[1] - x[1]))
    for i in range(1, len(tmp)):
        point = tmp[i]
        if not find_line(point, lines, 7):
            find_line_more(point, lines, len(lines), 7)
    return lines

#recursively fixes the lines in the case that one segment did not catch
def fix_lines(neighbors, segment):
    for neighbor in neighbors:
            if segment["line"] == neighbor["line"] and neighbor != segment:
                for seg_pt in segment["points"]:
                    for nei_pt in neighbor["points"]:
                        if distance(seg_pt, nei_pt) < 3:
                            for endpoint in segment["endpoints"]:
                                if endpoint not in neighbor["endpoints"]:
                                    neighbor["endpoints"].append(endpoint)
                            neighbor["points"] += segment["points"]
                            neighbors.remove(segment)
                            fix_lines(neighbors, neighbor)
                            return
    return

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
def create_mesh(segments, lines, points, xs, ys):
    point_dict = {}
    count = -1
    for point in points:
        point_dict[point] = (count := count + 1) 


    cLC = 1.0

    gmsh.initialize()

    gmsh.model.add("Moire")
    #gmsh.option.set_number("Mesh.SaveAll", 1)

    boundary_points = [(0, 0), (0, ys), (xs, ys), (xs, 0)]

    for key in point_dict:
        gmsh.model.geo.addPoint(key[0], key[1], 0, cLC, point_dict[key])

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
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.optimize("")
    gmsh.write("./Moire_BSpline.msh")
    gmsh.write("./Moire_BSpline.vtk")
    gmsh.finalize()