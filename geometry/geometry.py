from shapely import Polygon, MultiPolygon, unary_union, LineString, MultiLineString

import numpy as np   

from ..oop.observer import *

def shapely_to_coords(poly: MultiPolygon | Polygon) -> list[LineString] | LineString:
    if not isinstance(poly, MultiPolygon) and not isinstance(poly, Polygon):
        raise ValueError("input must be shapely polygon!")
    
    if isinstance(poly, MultiPolygon):
        poly = unary_union(poly.geoms)
    if isinstance(poly, MultiPolygon):
        from itertools import chain
        return list(chain.from_iterable(map(shapely_to_coords, poly.geoms)))
    elif isinstance(poly, Polygon):
        poly = poly.boundary
    
    if isinstance(poly, MultiLineString):
        return [p.coords for p in poly.geoms]
    else:
        return [poly.coords]

class MyPolygon(Observer):

    facecolor = observable()
    edgecolor = observable("black")
    linethickness = observable(2)
    label = observable()
    
    shape = observable(MultiPolygon())
    
    @listen("shape")
    def on_shape(self, shape : MultiPolygon, whose):
        if whose == self:
            # self.centroid = weight_avg(shape.geoms, weight="area", attr="centroid")
            self.centroid = shape.centroid
    
    def __init__(self, polygons):
        super().__init__(self.shape)
        self.shape = MultiPolygon(polygons)
    
class PolyObserver(Observer):
    @listen("shape")
    def on_shape(self, shape, who):
        print(who, "changed shape")
    
    def on_property(self, which : ObservableProperty, who):
        match which.name:
            case "facecolor":
                print("WHAt?")
            case "shape":
                pass
            case _:
                print(which.name, which._val)    

def get_midpoint(p1, p2, offset=None):
    from shapely.geometry import Point 
    
    p1 = np.array([p1.x, p1.y]) if isinstance(p1, Point) else np.array(p1)
    p2 = np.array([p2.x, p2.y]) if isinstance(p2, Point) else np.array(p2)
    
    midpoint = (p1 + p2) / 2
    
    if not offset:
        return [tuple(midpoint)]
    
    direction = p2 - p1
    perp_direction = np.array([-direction[1], direction[0]])
    perp_direction_norm = perp_direction / np.linalg.norm(perp_direction)
    dir = offset * perp_direction_norm
    
    return [tuple(midpoint - dir), tuple(midpoint + dir)]

# def is_convex(points):
#     from scipy.spatial import ConvexHull   
    
#     points = np.asarray(points)
    
#     if len(points) < 3:
#         return False
    
#     try:
#         hull = ConvexHull(points)
#         return len(hull.vertices) == len(points)
#     except:
#         return False
    
# def make_convex(points):
#     from shapely.geometry import Polygon
#     from scipy.spatial import ConvexHull   
    
#     points = np.asarray(points)
    
#     if len(points) < 3:
#         return None
    
#     try:
#         hull = ConvexHull(points)
        
#         if len(hull.vertices) == len(points):
#             hull_vertices = np.vstack([
#                 points[hull.vertices],
#                 points[hull.vertices[0]] 
#             ])
#             return Polygon(hull_vertices)
        
#         return None
    
#     except:
#         return None
    
if __name__ == "__main__":
    
    p = MyPolygon([(
        ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
        [((0.1,0.1), (0.1,0.2), (0.2,0.2), (0.2,0.1))]
    )])
    
    o = PolyObserver(*get_observables(p))
    
    p.facecolor = "anus"
    p.edgecolor = "dick"
    
    p.shape = MultiPolygon([(
        ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (10.0, 0.0)),
        [((0.1,0.1), (0.1,0.2), (0.2,0.2), (2.0,0.1))]
    )])
