import time
start_time = time.time()

import pyvista as pv
import yaml

from user_input import rectangles
from gen_design_sheet_metal.design_exploration.state import State
from gen_design_sheet_metal.design_exploration.plot_state import plot_state
from gen_design_sheet_metal.geometry.geometry import determine_fourth_point, calculate_planes, calculate_intersection, create_bending_point, calculate_flange_points

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import itertools

###########
# MAIN ####
###########    
if __name__ == "__main__":
    plot_cfg = cfg.get('plot', {})
    plotter = pv.Plotter()
    
    # Create Initial Rectangles. We always only have exactly 2 recaltes. Need 3 Points for each rect as Input. Convert it into a pyvista object to plot it
    # The input we get from "user_input.py" from rectangles. We still have to determine what that looks like
    rectangles = determine_fourth_point(rectangles)

    # Determine Planes
    planes = calculate_planes(rectangles)
    intersection = calculate_intersection(planes)

    initial_state = State(rectangles, planes, intersection)
    stack = [initial_state]
    solutions = []

    # --- Main search loop ---
    # In the search loop we want to check all combinations to connect points. The way we do that is by always picking 2 points of each rectangle, and try to connect them. If theyre invalid we pop these options
    while stack and len(solutions) < 150:
        state = stack.pop()

        rect0_points = list(state.rectangles[0].values())
        rect1_points = list(state.rectangles[1].values())

        rect0_combinations = list(itertools.combinations(rect0_points, 2))
        rect1_combinations = list(itertools.combinations(rect1_points, 2))

        for pair0 in rect0_combinations:
            for pair1 in rect1_combinations:
                new_state = state.copy()
                BP1 = create_bending_point(pair0[0], pair0[1], intersection)
                BP2 = create_bending_point(pair1[0], pair1[1], intersection)
                bending_points = [BP1, BP2]
                new_state.bending_points.extend(bending_points)
                #state.flange_points = calculate_flange_points(state.bending_points)
                # optionally: validate state here
                
                stack.append(new_state)
                solutions.append(new_state)

        # find flange points
        # create tabs

        


    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)} solutions")


    # --- Plotting solutions ---
    if not solutions:
        print("No valid solutions found.")
    else:
        solution_idx = [0]

        def show_solution(idx):
            plotter.clear()
            state = solutions[idx]
            # Optional: add combined mesh of all flanges
            #mesh = assemble_mesh(state)
            # Use unified plot function
            plot_state(state, plotter=plotter, cfg=plot_cfg, solution_idx=solution_idx, len_solutions=len(solutions))

        def key_press_callback(key):
            if key == 'Right':
                solution_idx[0] = (solution_idx[0] + 1) % len(solutions)
                show_solution(solution_idx[0])
            elif key == 'Left':
                solution_idx[0] = (solution_idx[0] - 1) % len(solutions)
                show_solution(solution_idx[0])

        plotter.add_key_event("Right", lambda: key_press_callback("Right"))
        plotter.add_key_event("Left", lambda: key_press_callback("Left"))
        show_solution(solution_idx[0])
        plotter.show()

        
