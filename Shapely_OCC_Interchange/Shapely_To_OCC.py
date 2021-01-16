from shapely.geometry import Polygon, LinearRing, MultiPolygon, GeometryCollection
from typing import Union, Iterator, List

from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.TopoDS import TopoDS_Face,TopoDS_Wire,TopoDS_Shape

from OCC.Extend.ShapeFactory import make_wire, make_edge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism

def pnt(p):
    return gp_Pnt(p[0], p[1], p[2])

def list_to_wire(points :List[List[float]]) -> TopoDS_Wire:
    wire = BRepBuilderAPI_MakePolygon()
    for point in points:
        wire.Add(pnt(point))
    wire.Close()
    return wire.Wire()

def line_ring_to_points(line_ring :LinearRing, z=0) -> List[List[float]]:
    #TODO: handle this in an arbetrary output coordinate system
    #rather than just the xy plane.
    return [[x,y,z] for x,y in zip(*line_ring.coords.xy)]

def polygon_to_face(polygon :Union[Polygon,MultiPolygon,GeometryCollection], z=0, keep_holes=True) -> Union[TopoDS_Face, List[TopoDS_Face]]:
    """ Returns a face from the passed polygon. Or multiple, if multiple were passed"""
    def inner(polygon):
        poly_points = line_ring_to_points(polygon.exterior, z=z)
        exterior_wire = list_to_wire(poly_points)
        #exterior_wire.Reverse()
        
        face_builder = BRepBuilderAPI_MakeFace(exterior_wire)
        
        if keep_holes:
            for interior in polygon.interiors:
                interior_points = line_ring_to_points(interior, z=z)
                interior_wire = list_to_wire(interior_points)
                #make it a hole by iterating the points in opposite direction:
                interior_wire.Reversed() 
                
                face_builder.Add( interior_wire )
        return face_builder.Face()
    if isinstance(polygon, MultiPolygon):
        r = []
        for p in polygon:
            r.append(inner(p))
            return r
    if isinstance(polygon, GeometryCollection):
        r = []
        for g in polygon:
            if isinstance(g, Polygon):
                r.append( inner(g) )
                return r
    return inner(polygon)