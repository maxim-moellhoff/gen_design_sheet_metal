import copy

class State:
    def __init__(self, rectangles, planes, bends, corner_points=None, flanges=None, points=None, elements=None):
        self.rectangles = rectangles
        self.planes = planes
        self.bends = bends
        self.corner_points = corner_points or []
        self.flanges = flanges or []
        self.points = points or {}
        self.elements = elements or []
        # self.bending_points = bending_points or []
        # self.tabs = tabs or []
        # self.flange_points = flange_points or {}

    def copy(self):
        return State(
            rectangles=copy.deepcopy(self.rectangles),
            planes=copy.deepcopy(self.planes),
            bends=copy.deepcopy(self.bends),
            corner_points=copy.deepcopy(self.corner_points),
            flanges=copy.deepcopy(self.flanges),
            points = copy.deepcopy(self.points),
            elements=copy.deepcopy(self.elements)
            # bending_points=copy.deepcopy(self.bending_points),
            # tabs=copy.deepcopy(self.tabs),
            # flange_points=copy.deepcopy(self.flange_points)
        )

    def __repr__(self):
        return (f"<State bends={len(self.flanges)}, tabs={len(self.tabs)}, "
                f"planes={len(self.planes)}, intersections={len(self.bends)}>")
