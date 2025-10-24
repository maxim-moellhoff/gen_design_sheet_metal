import numpy as np

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-9:
        return np.zeros_like(v)
    return v / n

def tangent_points_to_circle(P, C, r, normal):
    """
    Compute the two tangent points on circle (C,r) lying in plane with 'normal' from external point P.
    Return (T1, T2) or (None, None) if no tangent (P inside circle).
    """
    v = P - C
    d = np.linalg.norm(v)
    if d <= r + 1e-9:
        return None, None
    v = v / d

    # build orthonormal basis (x_axis, y_axis) in circle plane
    n = normalize(normal)
    # pick ref not parallel to n
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, n)) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    x_axis = normalize(np.cross(n, ref))
    y_axis = normalize(np.cross(n, x_axis))

    # coordinates of v in this basis
    vx = np.dot(v, x_axis)
    vy = np.dot(v, y_axis)
    alpha = np.arctan2(vy, vx)
    theta = np.arccos(r / d)

    ang1 = alpha + theta
    ang2 = alpha - theta

    T1 = C + r * (np.cos(ang1) * x_axis + np.sin(ang1) * y_axis)
    T2 = C + r * (np.cos(ang2) * x_axis + np.sin(ang2) * y_axis)
    return T1, T2

def line_intersection(P1, d1, P2, d2):
    """
    Solve P1 + s*d1 = P2 + t*d2 for s,t. Return intersection point and (s,t).
    If lines parallel/degenerate return (None, (None,None)).
    """
    A = np.column_stack([d1, -d2])
    b = (P2 - P1)
    if np.linalg.matrix_rank(A) < 2:
        return None, (None, None)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    s, t = sol[0], sol[1]
    I = P1 + s * d1
    return I, (s, t)

def point_in_triangle(p, a, b, c):
    """
    Barycentric technique to check if p inside triangle abc (including boundary).
    """
    v0 = c - a
    v1 = b - a
    v2 = p - a
    den = v0.dot(v0) * v1.dot(v1) - v0.dot(v1) ** 2
    if abs(den) < 1e-12:
        return False
    u = (v2.dot(v0) * v1.dot(v1) - v2.dot(v1) * v0.dot(v1)) / den
    v = (v2.dot(v1) * v0.dot(v0) - v2.dot(v0) * v0.dot(v1)) / den
    return (u >= -1e-9) and (v >= -1e-9) and (u + v <= 1 + 1e-9)

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