import itertools
from gen_design_sheet_metal.geometry.geometry import create_bending_point, calculate_flange_points, turn_points_into_element


def one_bend(state, solutions):
    rectangles = state.rectangles
    intersection = state.intersections

    rect0_points = list(rectangles[0].values())
    rect1_points = list(rectangles[1].values())

    rect0_combinations = list(itertools.permutations(rect0_points, 2))
    rect1_combinations = list(itertools.permutations(rect1_points, 2))

    state.elements.append(turn_points_into_element(rect0_points))

    for pair0 in rect0_combinations:
        for pair1 in rect1_combinations:
            new_state = state.copy()
            CP00 = pair0[0]
            CP01 = pair0[1]
            CP10 = pair1[0]
            CP11 = pair1[1]
            new_state.corner_points.extend([CP00,CP01,CP11,CP10])
            
            BP1 = create_bending_point(CP00, CP10, intersection)
            BP2 = create_bending_point(CP01, CP11, intersection)
            FP01, FP02, FP11, FP12 = calculate_flange_points(BP1, BP2, plane0=new_state.planes[0], plane1=new_state.planes[1])
            # new_state.bending_points.extend([BP1, BP2])
            new_state.bends = ({"bend_id": 0, "bend": intersection, "BP1": BP1, "BP2": BP2, 
                                    "FP01": FP01, "FP02": FP02, "FP11": FP11, "FP12": FP12})
            new_state.elements.append(turn_points_into_element([BP1, FP01, FP02, BP2]))
            new_state.elements.append(turn_points_into_element([BP1, FP11, FP12, BP2]))
            new_state.elements.append(turn_points_into_element(rect1_points))


            solutions.append(new_state)

        return solutions

# PATH 2: Two Bends. Up to 32 Solutions
def two_bends(state, solutions):
    return    