import Rhino.Geometry as rg
import math
import Rhino.RhinoDoc as rd

a = []
b = []
c = []


# Build Field of Play
FieldWidthInterval = rg.Interval(-0.5*FieldWidth, 0.5*FieldWidth)
FieldLengthInterval = rg.Interval(-0.5*FieldLength, 0.5*FieldLength)
FieldBoundary = rg.Rectangle3d(rg.Plane.WorldXY, FieldWidthInterval,FieldLengthInterval).ToPolyline()
a.append(FieldBoundary)
#FieldBoundaryCurve = FieldBoundary.ToNurbsCurve()
#FieldBoundaryPolyline = FieldBoundary.Polyline()
FieldBoundaryLines =  FieldBoundary.GetSegments()
#FieldBoundaryNURBSCurves = FieldBoundaryCurves.ToNurbsCurve()
# Fillet corners of field of play for Hockey and similar
def weave(weavelist1,weavelist2):
    wovenlist = []
    i = 0
    while i < len(weavelist1):
        wovenlist.append(weavelist1[i])
        wovenlist.append(weavelist2[i])
        i += 1
    return wovenlist
def corners(FieldBoundaryLines,CornerRadius):
    if(CornerRadius != False):
        FieldBoundaryCorners = []
        for i in range(len(FieldBoundaryLines)):
            FieldEdge = FieldBoundaryLines[i]
            if (i < 3):
                NextFieldEdge = FieldBoundaryLines[i + 1]
            else:
                NextFieldEdge = FieldBoundaryLines[0]

            # FieldEdgeEnd = FieldEdge.PointAtEnd()
            # NextFieldEdgeStart = NextFieldEdge.PointAtStart()
            FieldBoundaryFilletSet = rg.Curve.CreateFilletCurves(FieldEdge.ToNurbsCurve(), FieldEdge.To, NextFieldEdge.ToNurbsCurve(),
                                                                 NextFieldEdge.To, CornerRadius, False, True, False,
                                                                 rd.ActiveDoc.ModelAbsoluteTolerance,
                                                                 rd.ActiveDoc.ModelAbsoluteTolerance)
            #FieldFilletNum =
            FieldBoundaryFillet = FieldBoundaryFilletSet[-1]
            FieldBoundaryCorners.append(FieldBoundaryFillet)
            #b.append(FieldBoundaryCurves[0])
            #d.append(FieldBoundaryCurves[1])
            #c.extend(FieldBoundaryFillet)
        FieldBoundarySides = []
        for j in range(len(FieldBoundaryCorners)):
            FieldCorner = FieldBoundaryCorners[j]
            if(j < 3):
                NextFieldCorner = FieldBoundaryCorners[j+1]
            else:
                NextFieldCorner = FieldBoundaryCorners[0]
            #FieldCornerEnd =
            FieldBoundarySide = rg.Line(FieldCorner.ToNurbsCurve().PointAtEnd, NextFieldCorner.ToNurbsCurve().PointAtStart).ToNurbsCurve()
            FieldBoundarySides.append(FieldBoundarySide)
    Boundary = weave(FieldBoundaryCorners,FieldBoundarySides)
    JoinedBoundary = rg.Curve.JoinCurves(Boundary)
    return Boundary,JoinedBoundary


Output = corners(FieldBoundaryLines,FieldCornerRadius)
BoundaryCorners = Output[0]
BoundarySides = Output[1]
##         weave(FieldBoundaryCorners)
# Offset Focal Point
# if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
# if(SafetyZoneDimensions != False): #not all sports have safety zones, for example hockey
