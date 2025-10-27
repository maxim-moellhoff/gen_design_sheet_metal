import copy

class State:
    def __init__(self, rectangles, planes, intersections, corner_points=None, bends=None, elements=None):
        self.rectangles = rectangles
        self.planes = planes
        self.intersections = intersections
        self.corner_points = corner_points or []
        self.bends = bends or {}
        self.elements = elements or []
        # self.bending_points = bending_points or []
        # self.tabs = tabs or []
        # self.flange_points = flange_points or {}

    def copy(self):
        return State(
            rectangles=copy.deepcopy(self.rectangles),
            planes=copy.deepcopy(self.planes),
            intersections=copy.deepcopy(self.intersections),
            corner_points=copy.deepcopy(self.corner_points),
            bends=copy.deepcopy(self.bends),
            elements=copy.deepcopy(self.elements)
            # bending_points=copy.deepcopy(self.bending_points),
            # tabs=copy.deepcopy(self.tabs),
            # flange_points=copy.deepcopy(self.flange_points)
        )

    def __repr__(self):
        return (f"<State bends={len(self.bends)}, tabs={len(self.tabs)}, "
                f"planes={len(self.planes)}, intersections={len(self.intersections)}>")
