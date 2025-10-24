from gen_design_sheet_metal.geometry.utilities import normalize
import pyvista as pv
import numpy as np
from gen_design_sheet_metal.design_rules import min_dist_mount_bend

def plot_state(state, plotter=None, cfg=None, solution_idx=None, len_solutions=None):
    """
    Unified plotting function for flanges, tabs, BP points, and optional plane/debug info.
    """

    if plotter is None or cfg is None:
        return
    
    if cfg.get('Rectangle', True):
        for i, rect in enumerate(state.rectangles):
            # Extract the points as an ordered list of vertices (A–B–C–D)
            pts = np.array([rect["pointA"], rect["pointB"], rect["pointC"], rect["pointD"]])

            # Define the face: first value = number of points in the face
            faces = np.hstack([[4, 0, 1, 3, 2]])

            # Create the PyVista mesh
            rectangle_mesh = pv.PolyData(pts, faces)

            # Add to plotter
            plotter.add_mesh(rectangle_mesh, color="blue", opacity=0.6, show_edges=True)


    if cfg.get('Planes', True):
        plane_size = 3  # adjust size of the plane
        for _, plane in enumerate(state.planes):
            # Create PyVista plane
            plane_mesh = pv.Plane(center=plane.position, direction=plane.orientation, i_size=plane_size, j_size=plane_size)
            plotter.add_mesh(plane_mesh, color="#8FAADC", opacity=0.4, show_edges=True)

    if cfg.get('Intersections', True):
        L = 2.0  # length of line in both directions from bend point, adjust as needed
        for intersection in state.intersections:
            point_on_line = intersection.get("point")
            d = normalize(intersection.get("direction", np.array([1,0,0])))
            intersection_id = intersection.get("id", "N/A")

            if point_on_line is not None and d is not None:
                # create line along bend direction
                line = pv.Line(point_on_line - d * L, point_on_line + d * L)
                plotter.add_mesh(line, color="#E9DA38", line_width=8)

                # optionally label the bend
                if cfg.get('debug_labels', False):
                    plotter.add_point_labels(np.array([point_on_line]), [intersection_id], font_size=20, point_color="#E9DA38", text_color="black")


    if cfg.get('Bends', True):
        L = 2.0  # length of line in both directions from bend point, adjust as needed
        for bend in state.bend:
            point_on_line = bend.get("point")
            d = normalize(bend.get("direction", np.array([1,0,0])))
            bend_id = bend.get("id", "N/A")

            if point_on_line is not None and d is not None:
                # create line along bend direction
                line = pv.Line(point_on_line - d * L, point_on_line + d * L)
                plotter.add_mesh(line, color="#E9DA38", line_width=8)

                # optionally label the bend
                if cfg.get('debug_labels', False):
                    plotter.add_point_labels(np.array([point_on_line]), [bend_id], font_size=20, point_color="#E9DA38", text_color="black")

    # --- Flanges and BP points ---
    # BP points
    if cfg.get('Bending Points', True):
        BP1 = state.bending_points[0]
        BP2 = state.bending_points[1]
        plotter.add_points(BP1, color=cfg.get('BP1_color','red'), point_size=20)
        plotter.add_points(BP2, color=cfg.get('BP2_color','blue'), point_size=20)
        if cfg.get('debug_labels', True):
            plotter.add_point_labels(BP1, ["BP1"], font_size=20, point_color='red', text_color='red')
            plotter.add_point_labels(BP2, ["BP2"], font_size=20, point_color='blue', text_color='blue')

    if solution_idx is not None and len_solutions is not None:
        counter_text = f"Solution: {solution_idx}/{len_solutions}"
        # position options: upper_left, upper_right, lower_left, lower_right
        plotter.add_text(counter_text, position="upper_left",
                            font_size=14, color="black", shadow=False)



    # --- Finish plot ---
    plotter.show_grid()
    # plotter.camera_position = 'iso'
    plotter.render()

"""
    # --- Flanges and BP points ---
    for bend_id, flange in state.flange_points.items():
        # BP points
        if cfg.get('Bending Points', True):
            pt_BP0 = np.array([flange["BP0"]])
            pt_BP1 = np.array([flange["BP1"]])
            pt_BP2 = np.array([flange["BP2"]])
            plotter.add_points(pt_BP0, color=cfg.get('BP0_color','green'), point_size=20)
            plotter.add_points(pt_BP1, color=cfg.get('BP1_color','red'), point_size=20)
            plotter.add_points(pt_BP2, color=cfg.get('BP2_color','blue'), point_size=20)
            if cfg.get('debug_labels', False):
                plotter.add_point_labels(pt_BP0, [f"{bend_id}_BP0"], font_size=20, point_color='green', text_color='red')
                plotter.add_point_labels(pt_BP1, [f"{bend_id}_BP1"], font_size=20, point_color='red', text_color='red')
                plotter.add_point_labels(pt_BP2, [f"{bend_id}_BP2"], font_size=20, point_color='blue', text_color='blue')

        # Flange corners
        if cfg.get('Flange', True):
            for pt_name in ["FPA1", "FPA2", "FPB1", "FPB2"]:
                pt = np.array([flange[pt_name]])
                color = cfg.get(f'{pt_name}_color', 'green')
                plotter.add_points(pt, color=color, point_size=8)
                if cfg.get('debug_labels', False):
                    plotter.add_point_labels(pt, [f"{bend_id}_{pt_name}"], font_size=20, point_color=color, text_color=color)

        # Plane quads
        if cfg.get('Quads', True):
            for quad, color in zip([flange["planeA_quad"], flange["planeB_quad"]],
                                   [cfg.get('planeA_color','#EC11E5'),
                                    cfg.get('planeB_color','#F0AC53')]):
                if quad is not None and len(quad) >= 4:
                    quad = np.array(quad)
                    faces = np.hstack([[4, 0, 1, 2, 3]])
                    plotter.add_mesh(pv.PolyData(quad, faces), color=color, opacity=0.35)

    # --- Tabs ---
    if cfg.get('Tabs', True):
        pts = np.array(state.tabs_faces["points"])
        faces = np.array(state.tabs_faces["faces"])
        if len(pts) > 0 and len(faces) > 0:
            plotter.add_mesh(pv.PolyData(pts, faces), color="#5F94FF", opacity=0.6, show_edges=True)

            if cfg.get('debug_labels', True):
                # Label each tab by bend_id and type
                for tab in getattr(state, 'tabs', []):
                    tab_label = f"plane ({tab['type']})"
                    for poly in tab['polys']:
                        mid = np.mean(poly, axis=0)
                        plotter.add_point_labels([mid], [tab_label], font_size=20, point_color='yellow', text_color='black')

    """
