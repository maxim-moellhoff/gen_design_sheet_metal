import itertools
from gen_design_sheet_metal.geometry.geometry import create_bending_point, calculate_flange_points, turn_points_into_element
from gen_design_sheet_metal.geometry.utilities import check_cross_within

def one_bend(state, solutions):
    rectangles = state.rectangles
    intersection = state.intersections

    rectA_points = list(rectangles[0].values())
    rectB_points = list(rectangles[1].values())

    rectA_combinations = list(itertools.permutations(rectA_points, 2))
    rectB_combinations = list(itertools.permutations(rectB_points, 2))

    state.elements.append(turn_points_into_element(rectA_points))

    for pairA in rectA_combinations:
        for pairB in rectB_combinations:
            new_state = state.copy()
            CPA1 = pairA[0]
            CPA2 = pairA[1]
            CPB1 = pairB[0]
            CPB2 = pairB[1]
            if check_cross_within(CPA1, CPA2, CPB1, CPB2): continue
            new_state.corner_points.extend([CPA1,CPA2,CPB2,CPB1])
            
            BP1 = create_bending_point(CPA1, CPB1, intersection)
            BP2 = create_bending_point(CPA2, CPB2, intersection)
            FPA1, FPA2, FPB1, FPB2 = calculate_flange_points(BP1, BP2, planeA=new_state.planes[0], planeB=new_state.planes[1])
            # new_state.bending_points.extend([BP1, BP2])
            new_state.bends = ({"bend_id": 0, "bend": intersection, "BP1": BP1, "BP2": BP2, 
                                    "FPA1": FPA1, "FPA2": FPA2, "FPB1": FPB1, "FPB2": FPB2})
            new_state.elements.append(turn_points_into_element([CPA1, FPA1, FPA2, CPA2]))
            new_state.elements.append(turn_points_into_element([BP1, FPA1, FPA2, BP2]))
            new_state.elements.append(turn_points_into_element([BP1, FPB1, FPB2, BP2]))
            new_state.elements.append(turn_points_into_element([CPB1, FPB1, FPB2, CPB2]))
            new_state.elements.append(turn_points_into_element(rectB_points))

            solutions.append(new_state)

        return solutions

# PATH 2: Two Bends. Up to 32 Solutions
def two_bends(state, solutions):
    return    