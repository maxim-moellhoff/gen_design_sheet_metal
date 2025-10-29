import itertools
from gen_design_sheet_metal.geometry.part_generation import calculate_planes, calculate_intersections, create_bending_point, calculate_flange_points, turn_points_into_element, determine_fourth_points
from gen_design_sheet_metal.geometry.utilities import check_lines_cross, normalize
from gen_design_sheet_metal.design_rules import min_flange_width

import numpy as np

def one_bend(state, solutions):
    rectangles = state.rectangles
    intersection = state.intersections
    state.bends.append(intersection)

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
            
            new_state.corner_points.extend([CPA1,CPA2,CPB2,CPB1])
            
            BP1 = create_bending_point(CPA1, CPB1, intersection)
            BP2 = create_bending_point(CPA2, CPB2, intersection)

            if check_lines_cross(CPA1, CPA2, CPB1, CPB2, BP1, BP2): continue

            FPA1, FPA2, FPB1, FPB2 = calculate_flange_points(BP1, BP2, planeA=new_state.planes[0], planeB=new_state.planes[1])

            new_state.bends.append({"bend_id": 0, "bend": intersection, "BP1": BP1, "BP2": BP2, 
                                    "FPA1": FPA1, "FPA2": FPA2, "FPB1": FPB1, "FPB2": FPB2})
            new_state.elements.append(turn_points_into_element([CPA1, FPA1, FPA2, CPA2]))
            new_state.elements.append(turn_points_into_element([BP1, FPA1, FPA2, BP2]))
            new_state.elements.append(turn_points_into_element([BP1, FPB1, FPB2, BP2]))
            new_state.elements.append(turn_points_into_element([CPB1, FPB1, FPB2, CPB2]))
            new_state.elements.append(turn_points_into_element(rectB_points))

            solutions.append(new_state)

        return solutions

# If there are two bends, there are three planes, which are called A, B and C
# The first rectangle the user provides is A, and the second one is C, and the one in between B
def two_bends(state, solutions):
    rectangles = state.rectangles
    planeA = state.planes[0]
    planeC = state.planes[1]

    rectA_points = list(rectangles[0].values())
    rectC_points = list(rectangles[1].values())

    rectA_combinations = list(itertools.permutations(rectA_points, 2))
    rectC_combinations = list(itertools.permutations(rectC_points, 2))

    state.elements.append(turn_points_into_element(rectA_points))

    for pairA in rectA_combinations:
        BPA1 = pairA[0]
        BPA2 = pairA[1]
        for i, BPC0 in enumerate(rectC_points):
            triangle = {"pointA": BPA1, "pointB": BPA2, "pointC": BPC0}
            rectangle = determine_fourth_points([triangle])

            new_state = state.copy()
            CPA1 = BPA1
            CPB1 = BPA2
            CPC0 = BPC0
            
            new_state.corner_points.extend([CPA1,CPB1,CPC0])
            
            planeB = calculate_planes(rectangles=rectangle)[0]
            bendAB = calculate_intersections(planes=[planeA, planeB])
            bendBC = calculate_intersections(planes=[planeB, planeC])
            
            dir_vector = np.cross(planeB.orientation, bendAB["direction"])
            dir_vector /= np.linalg.norm(dir_vector)
            
            # creat Flange points for side A on plane B
            FPAB1 = BPA1 - min_flange_width/2 * dir_vector
            FPAB2 = BPA2 - min_flange_width/2 * dir_vector
            
            # create BP1 and BP2 for Side C
            CPC1 = rectC_points[(i + 1) % 4]
            CPC2 = rectC_points[(i - 1) % 4]
            create_bending_point(CPC1, FPAB1, bendBC)
            create_bending_point(CPC2, FPAB2, bendBC)

            # Create Flange points for side C on plane B
            BPC1 = BPC0 + np.linalg.norm(BPA1 - BPA2)/2 * normalize(bendBC["direction"])
            BPC2 = BPC0 - np.linalg.norm(BPA1 - BPA2)/2 * normalize(bendBC["direction"])
            
            FPBC1, FPBC2, FPC1, FPC2 = calculate_flange_points(BPC1, BPC2, planeB, planeC)

            # # create Elements rectA, FlangeA, rectB, Flange C, rectC
            new_state.flanges.append({"bend_id": 0, "bend": bendAB, "BP1": BPA1, "BP2": BPA2, 
                                    "FPA1": FPAB1, "FPA2": FPAB2, "FPB1": FPAB1, "FPB2": FPAB2})
            new_state.flanges.append({"bend_id": 1, "bend": bendBC, "BP1": BPC1, "BP2": BPC2,
                                      "FPBC1": FPBC1, "FPBC2": FPBC2, "FPC1": FPC1, "FPC2": FPC2})

            new_state.elements.append(turn_points_into_element([BPA1, FPAB1, FPAB2, BPA2]))
            new_state.elements.append(turn_points_into_element([FPAB2, FPBC1, FPBC2, FPAB1]))
            new_state.elements.append(turn_points_into_element([FPBC1, BPC1, BPC2, FPBC2]))
            new_state.elements.append(turn_points_into_element([BPC1, CPC1, CPC2, BPC2]))

            solutions.append(new_state)

    for pairB in rectC_combinations:
        for BPA1 in rectA_points:
            continue

    return solutions