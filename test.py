       for node in line["nodes"]:
            coords = node["coord"]
            close = sorted(points, key = lambda x : (x[0] - coords[0]) ** 2 + (x[0] - coords[0]) ** 2)
            for i in range(2):
                segment = {}
                segment["endpoints"] = []
                segment["endpoints"].append(node)
                segment["points"] = []
                segment["color"] = line["color"]
                last = close[0]
                if distance(last, coords) > 40:
                    continue

                for point in close:
                    if distance(point, last) > 15:
                        continue
                    else:
                        segment["points"].append(point)
                        last = point
                        points.remove(point)
                        close.remove(point)

                for other_node in line["nodes"]:
                    if distance(other_node["coord"], last) < 15:
                        segment["endpoints"].append(other_node)
                
                segments.append(segment)

    print(len(segments))

    accum = []
    for i in range(len(segments)):
        accum.append(segments[i]["points"])
        for endpoint in segments[i]["endpoints"]:
            accum.append([endpoint["coord"]])
    print_lines(accum) 