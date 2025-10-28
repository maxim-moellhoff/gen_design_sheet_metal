import numpy as np

def convert_to_float64(items):
    """Convert all list-based item points to numpy float64 arrays."""
    converted = []
    for item in items:
        new_item = {}
        for key, value in item.items():
            arr = np.array(value, dtype=np.float64)
            new_item[key] = arr
        converted.append(new_item)
    return converted

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-9:
        return np.zeros_like(v)
    return v / n

def closest_points_between_lines(p1, d1, p2, d2):
    d1 = normalize(d1)
    d2 = normalize(d2)
    r = p1 - p2
    a = np.dot(d1, d1)
    b = np.dot(d1, d2)
    c = np.dot(d2, d2)
    e = np.dot(d1, r)
    f = np.dot(d2, r)
    denom = a * c - b * b
    if abs(denom) < 1e-9:
        t = 0.0
        s = np.dot(d2, (p1 - p2))
        pt1 = p1 + t * d1
        pt2 = p2 + s * d2
        return pt1, pt2, t, s
    t = (b * f - c * e) / denom
    s = (a * f - b * e) / denom
    pt1 = p1 + t * d1
    pt2 = p2 + s * d2

    return pt1, pt2, t, s

def perp_toward_plane(plane, BP0, bend_dir):
    n = plane.orientation
    # bend_dir = plane.orientation
    perp = np.cross(n, bend_dir)
    if np.linalg.norm(perp) < 1e-9:
        perp = np.cross(bend_dir, np.array([1,0,0]))
        if np.linalg.norm(perp) < 1e-9:
            perp = np.cross(bend_dir, np.array([0,1,0]))
    perp = normalize(perp)
    sign = np.sign(np.dot(plane.position - BP0, perp))
    if sign == 0:
        sign = 1.0
    return perp * sign

from shapely.geometry import LineString, Polygon

def check_lines_cross(CPA1, CPA2, CPB1, CPB2, BP1, BP2):
    """
    Returns true, if the input is cross free, and therefore valid
    """
    # Define the lines
    LineA1 = LineString([CPA1, BP1])
    LineA2 = LineString([CPA2, BP2])
    LineB1 = LineString([BP1, CPB1])
    LineB2 = LineString([BP2, CPB2])
    
    # Find intersection of the two lines
    inter1 = LineA1.intersection(LineA2)
    inter2 = LineB1.intersection(LineB2)
    intersection_free = inter1.is_empty and inter2.is_empty
    if intersection_free: return False

   # Define the quadrilateral (the region of interest)
    quad1 = Polygon([CPA1, BP1, BP2, CPA2])
    quad2 = Polygon([CPB1, BP1, BP2, CPB2])
    if inter1.within(quad1): return True
    if inter2.within(quad2): return True

    return False