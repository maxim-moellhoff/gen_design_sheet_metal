from gen_design_sheet_metal.design_rules import min_dist_mount_bend, min_flange_width, min_flange_length
import numpy as np
import pyvista as pv
from types import SimpleNamespace
from gen_design_sheet_metal.geometry.utilities import normalize, tangent_points_to_circle, line_intersection, point_in_triangle, closest_points_between_lines

def determine_fourth_point(rectangles):
    """
    Given three points (A, B, C), compute fourth point D.
    Assumes points are arbitrary corners of a rectangle.
    """
    for _, rect in enumerate(rectangles):
        A, B, C = rect["pointA"], rect["pointB"], rect["pointC"]
        AB = B - A
        AC = C - A
        D = A + AB + AC
        rect["pointD"] = D 

    return rectangles

def calculate_planes(rectangles):
    """
    Given a list of rectangles defined by three points (A, B, C),
    compute the position (centroid) and orientation (normal vector)
    of each corresponding plane.
    
    Returns:
        dict: {
            "Plane[0]": {"position": np.ndarray, "normal": np.ndarray},
            "Plane[1]": {"position": np.ndarray, "normal": np.ndarray}
        }
    """
    planes = []

    for i, rect in enumerate(rectangles):
        A, B, C = rect["pointA"], rect["pointB"], rect["pointC"]

        # Compute normal vector
        AB = B - A
        AC = C - A
        normal = normalize(np.cross(AB, AC))

        # Compute centroid (plane position)
        position = (A + B + C) / 3

        planes.append(SimpleNamespace(position=position, orientation=normal))


    return planes

def calculate_intersection(planes):
    intersections = []

    n1, n2 = planes[0].orientation, planes[1].orientation
    p01, p02 = planes[0].position, planes[1].position

    direction = np.cross(n1, n2)
    direction = normalize(direction)
    
    A = np.vstack([n1, n2, direction])
    b = np.array([np.dot(n1, p01), np.dot(n2, p02), 0.0])

    point = np.linalg.lstsq(A, b, rcond=None)[0]

    intersections.append({
        "point": point,
        "direction": direction
    })
    return intersections

def create_bending_point(point0, point1, intersection):
    point_on_intersection = intersection[0]['point']
    direction_intersection = intersection[0]['direction']
    p0 = point0
    p1 = point1
    dir_AB = p1 - p0
    if np.linalg.norm(dir_AB) < 1e-9:
        vec = p0 - point_on_intersection
        t = np.dot(vec, direction_intersection)
        BP = point_on_intersection + t * direction_intersection
    else:
        dir_AB = normalize(dir_AB)
        pt_on_bend, _, _, _ = closest_points_between_lines(
            point_on_intersection, direction_intersection, p0, dir_AB
        )
        BP = pt_on_bend
        
    return BP

def calculate_flange_points(bends, planes, bending_points, flange_width=min_flange_width):
    flange_points = {}
    for bend in bends:
        bend_id = bend.get("id")
        BP = bending_points.get(bend_id)
        if BP is None:
            continue
        BP0, BP1, BP2 = BP["BP0"], BP["BP1"], BP["BP2"]
        bend_dir = normalize(BP2 - BP1)
        if np.linalg.norm(bend_dir) < 1e-9:
            continue
        mid = (BP1 + BP2) / 2.0
        planeA_id, planeB_id = bend.get("planes")
        planeA = planes[planeA_id]
        planeB = planes[planeB_id]

        def perp_toward_plane(plane):
            n = plane.orientation
            perp = np.cross(n, bend_dir)
            if np.linalg.norm(perp) < 1e-9:
                perp = np.cross(bend_dir, np.array([1,0,0]))
                if np.linalg.norm(perp) < 1e-9:
                    perp = np.cross(bend_dir, np.array([0,1,0]))
            perp = normalize(perp)
            sign = np.sign(np.dot(plane.position - mid, perp))
            if sign == 0:
                sign = 1.0
            return perp * sign

        perpA = perp_toward_plane(planeA)
        perpB = perp_toward_plane(planeB)
        half = flange_width / 2.0

        FPA1, FPA2 = BP1 + perpA * half, BP2 + perpA * half
        FPB1, FPB2 = BP1 + perpB * half, BP2 + perpB * half
        BPA1, BPA2 = BP1.copy(), BP2.copy()
        BPB1, BPB2 = BP1.copy(), BP2.copy()

        planeA_quad = np.array([FPA1, FPA2, BPA2, BPA1])
        planeB_quad = np.array([FPB1, FPB2, BPB2, BPB1])

        flange_points[bend_id] = {"BP0": BP0, "BP1": BP1, "BP2": BP2, "FPA1": FPA1, "FPA2": FPA2,
                                  "FPB1": FPB1, "FPB2": FPB2,
                                  "planeA_quad": planeA_quad, "planeB_quad": planeB_quad}

    return flange_points