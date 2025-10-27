import time
start_time = time.time()

import pyvista as pv
import yaml

from user_input import rect0, rect1
from .design_exploration.state import State
from .design_exploration.plot_state import plot_state
from .geometry.utilities import convert_to_float64
from .geometry.geometry import determine_fourth_point, calculate_planes, calculate_intersection, collision_tab_bend
from .design_exploration.connect_edges import one_bend, two_bends
with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

def main():
    # ------ Initialization ------
    plot_cfg = cfg.get('plot', {})
    plotter = pv.Plotter()
    
    # ------ Initial Calculations ------
    rectangles_input = convert_to_float64(items=[rect0, rect1])
    rectangles = determine_fourth_point(rectangles_input)
    planes = calculate_planes(rectangles)
    intersection = calculate_intersection(planes)

    # ------ Design Exploration ------
    state = State(rectangles, planes, intersection)
    solutions = []
    
    if not collision_tab_bend(intersection, rectangles) and cfg.get('design_exploration').get('single_bend', True):
        solutions.append(one_bend(state, solutions))
    
    solutions.append(two_bends(state, solutions))

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)-1} solutions")

    # ------ Plotting solutions ------
    if len(solutions)==1: return
    plot_state(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()
