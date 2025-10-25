import time
start_time = time.time()

import pyvista as pv
import yaml

from user_input import rect0, rect1
from .design_exploration.state import State
from .design_exploration.plot_state import plot_state
from .geometry.geometry import determine_fourth_point, calculate_planes, calculate_intersection, create_bending_point, calculate_flange_points, collision_tab_bend
from .design_exploration.connect_edges import one_bend, two_bends
with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import itertools

if __name__ == "__main__":
    plot_cfg = cfg.get('plot', {})
    plotter = pv.Plotter()
    
    # Create Initial Rectangles. We always only have exactly 2 rectangles. Need 3 Points for each rect as Input. Convert it into a pyvista object to plot it
    # The input we get from "user_input.py" from rectangles. We still have to determine what that looks like
    rectangles = determine_fourth_point([rect0, rect1])
    planes = calculate_planes(rectangles)
    intersection = calculate_intersection(planes)

    # Design Exploration
    state = State(rectangles, planes, intersection)

    solutions = []
    
    if not collision_tab_bend(intersection, rectangles):
        solutions.append(one_bend(state, solutions))
    
    solutions.append(two_bends(state, solutions))

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)} solutions")

    # ------ Plotting solutions ------
    if not solutions:
        print("No valid solutions found.")
    else:
        solution_idx = [0]
        def show_solution(idx):
            plotter.clear()
            state = solutions[idx]
            #mesh = assemble_mesh(state)
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

        
