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
FieldBoundaryCurves =  FieldBoundary.GetSegments()
#FieldBoundaryNURBSCurves = FieldBoundaryCurves.ToNurbsCurve()
# Fillet corners of field of play for Hockey and similar
if(CornerRadius != False):
    FieldBoundaryCorners = []
    for i in range(len(FieldBoundaryCurves)):
        FieldEdge = FieldBoundaryCurves[i]
        if (i < 3):
            NextFieldEdge = FieldBoundaryCurves[i + 1]
        else:
            NextFieldEdge = FieldBoundaryCurves[0]

        # FieldEdgeEnd = FieldEdge.PointAtEnd()
        # NextFieldEdgeStart = NextFieldEdge.PointAtStart()
        FieldBoundaryFilletSet = rg.Curve.CreateFilletCurves(FieldEdge.ToNurbsCurve(), FieldEdge.To, NextFieldEdge.ToNurbsCurve(),
                                                             NextFieldEdge.To, CornerRadius, False, True, False,
                                                             rd.ActiveDoc.ModelAbsoluteTolerance,
                                                             rd.ActiveDoc.ModelAbsoluteTolerance)
        [x[1] for x in FieldBoundaryFilletSet]
        FieldBoundaryCorners.extend(FieldBoundaryFillet)
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
        #FieldBoundarySide = rg.Line(FieldCorner.PointAtEnd, NextFieldCorner.PointAtStart)
        #FieldBoundarySides.append(FieldBoundarySide)
# Offset Focal Point
#if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
#if(SafetyZoneDimensions != False): #not all sports have safety zones, for example hockey


