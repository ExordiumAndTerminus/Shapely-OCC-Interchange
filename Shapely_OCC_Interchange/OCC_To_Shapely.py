import collections
from shapely.geometry import Polygon
from OCC.Core.BRepTools import BRepTools_WireExplorer, breptools_OuterWire
from OCC.Extend.TopologyUtils import discretize_edge, discretize_wire, TopologyExplorer
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_WIRE, TopAbs_INTERNAL, TopAbs_SHAPE
from OCC.Core.TopoDS import TopoDS_Face

#TODO: fix up type hinting for this file!!
#Functions for converting back and forth between Shapely and Python OCC

'''
converts ordered dictionary to list - preserves order of input
'''
def orderedDict_To_List(oDict):
    edges = []
    for item in oDict.keys():
        edges.append(item)
    return edges

def getPointsFromWire(wire):
    edgesDict = collections.OrderedDict()
    previous = 0
    wireExp = BRepTools_WireExplorer(wire)
    while wireExp.More():
        temp = discretize_edge(wireExp.Current())
        if previous != 0:
        #check to make sure the shared vertex coordinate is first, reverse if not (arcs have this issue)
            if previous != temp[0]:
                temp2=temp
                temp2.reverse()
                temp = temp2
                previous = temp[-1]
        else: previous = temp[-1]

    #add the coordinates in order to the list, ignore value as we only care about the key
        for coord in temp:
            edgesDict[coord] = 0
        wireExp.Next()
    points = orderedDict_To_List(edgesDict)
    return points

'''
takes in topoDS_Face and returns shapely Polygon
'''
def getPointsFromFace(face):
    holes = []
    wiresToDiscretize = TopExp_Explorer(face, TopAbs_WIRE)
    #if face has no holes, retrieve only wire and grab points
    wiresToDiscretize.Next()
    noHoles = not wiresToDiscretize.More()
    if noHoles:
        #reinitialize the explorer since we can't go back...
        wiresToDiscretize = TopExp_Explorer(face, TopAbs_WIRE).Current()
        points = getPointsFromWire(wiresToDiscretize)
        return points
    
    #need to figure out which is outline and which are holes, discretize all wires first
    else:
        outerWire = breptools_OuterWire(face)
        shape = getPointsFromWire(outerWire)

        wiresToDiscretize = TopExp_Explorer(face, TopAbs_WIRE)
        while wiresToDiscretize.More():
            holes.append(getPointsFromWire(wiresToDiscretize.Current()))
            wiresToDiscretize.Next()
        
        #remove the outerwire from the hole collection - once found, break the loop
        for item in holes:
            if item[0] == shape[0]:
                holes.remove(item)
                break

        return shape, holes

def Face_to_Polygon(face:TopoDS_Face) -> Polygon:
    outline, holes = getPointsFromFace(face)
    poly = Polygon(outline, holes)
    return poly