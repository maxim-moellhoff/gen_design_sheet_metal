import itertools
from gen_design_sheet_metal.geometry.geometry import create_bending_point, calculate_flange_points


def one_bend(state, solutions):
    rectangles = state.rectangles
    intersection = state.intersections

    # PATH 1: One Bend. Up to 144 Solutions
    rect0_points = list(rectangles[0].values())
    rect1_points = list(rectangles[1].values())

    rect0_combinations = list(itertools.permutations(rect0_points, 2))
    rect1_combinations = list(itertools.permutations(rect1_points, 2))

    for pair0 in rect0_combinations:
        for pair1 in rect1_combinations:
            new_state = state.copy()
            CP00 = pair0[0]
            CP01 = pair0[1]
            CP10 = pair1[0]
            CP11 = pair1[1]
            
            BP1 = create_bending_point(CP00, CP10, intersection)
            BP2 = create_bending_point(CP01, CP11, intersection)
            new_state.bending_points.extend([BP1, BP2])
            new_state.corner_points.extend([CP00,CP01,CP11,CP10])
            
            # FP01, FP02, FP11, FP12 = calculate_flange_points(bends=new_state.intersections, planes=new_state.planes, bending_points=new_state.bending_points)

            solutions.append(new_state)

        return solutions

# PATH 2: Two Bends. Up to 32 Solutions
def two_bends(state, solutions):
    return    