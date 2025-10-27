from gen_design_sheet_metal.design_rules import min_dist_mount_bend, min_flange_width, min_flange_length
import numpy as np
import pyvista as pv
from types import SimpleNamespace
from gen_design_sheet_metal.geometry.utilities import normalize, closest_points_between_lines, perp_toward_plane

def determine_fourth_point(rectangles):
    """
    Given three points (A, B, C), compute fourth point D and reorder the points
    in circular order (A, B, D, C) so the rectangle is not twisted.
    """
    for rect in rectangles:
        A, B, C = rect["pointA"], rect["pointB"], rect["pointC"]

        # Compute vectors
        AB = B - A
        AC = C - A

        # Compute normal (for consistent orientation)
        normal = np.cross(AB, AC)

        # If AB and AC are swapped (zigzag), flip AC to keep CCW order
        if np.dot(np.cross(AB, AC), normal) < 0:
            # Swap B and C if needed
            B, C = C, B
            AB = B - A
            AC = C - A

        # Compute D in the proper rectangular order
        D = A + AB + AC

        # Overwrite in consistent circular order (A, B, D, C)
        rect["pointA"] = A
        rect["pointB"] = B
        rect["pointC"] = D
        rect["pointD"] = C

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

def collision_tab_bend(bend, rectangles):
    return False

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

def calculate_flange_points(BP1, BP2, plane0, plane1, flange_width=min_flange_width):
    # bend_dir = normalize(BP2 - BP1)
    
    BP0 = (BP1 + BP2) / 2.0
    perpA = perp_toward_plane(plane0, BP0)
    perpB = perp_toward_plane(plane1, BP1)
    half = flange_width / 2.0

    FP01, FP02 = BP1 + perpA * half, BP2 + perpA * half
    FP11, FP12 = BP1 + perpB * half, BP2 + perpB * half

    # planeA_quad = np.array([FP01, FP02, BPA2, BPA1])
    # planeB_quad = np.array([FP11, FP12, BPB2, BPB1])

    # flange_points[bend_id] = {"BP0": BP0, "BP1": BP1, "BP2": BP2, "FPA1": FPA1, "FPA2": FPA2,
    #                           "FPB1": FPB1, "FPB2": FPB2,
    #                           "planeA_quad": planeA_quad, "planeB_quad": planeB_quad}
    flange_points = [FP01, FP02, FP11, FP12]

    return FP01, FP02, FP11, FP12

def turn_points_into_element(points):
    points = np.array(points, dtype=np.float64)

    n_points = len(points)
    if n_points not in (3, 4):
        raise ValueError(f"Expected 3 or 4 points, got {n_points}")

    # PyVista faces: [n_points, p0, p1, ..., pN]
    faces = np.hstack([[n_points], np.arange(n_points)])
    mesh = pv.PolyData(points, faces)

    return mesh
