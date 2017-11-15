import Rhino.Geometry as rg
import math
import Rhino.RhinoDoc as rd

a = []
b = []
c = []


# Helper Functions


def weave(weavelist1, weavelist2):
    wovenlist = []
    i = 0
    while i < len(weavelist1):
        wovenlist.append(weavelist1[i])
        wovenlist.append(weavelist2[i])
        i += 1
    return wovenlist


# Process Functions

def field(field_length, field_width):
    field_width_interval = rg.Interval(-0.5*field_width, 0.5*field_width)
    field_length_interval = rg.Interval(-0.5*field_length, 0.5*field_length)
    field_boundary = rg.Rectangle3d(rg.Plane.WorldXY, field_width_interval, field_length_interval).ToPolyline()
    field_boundary_lines = field_boundary.GetSegments()
    return field_boundary, field_boundary_lines


def corners(field_boundary_lines, corner_radius):
    if corner_radius is not False:
        field_boundary_corners = []
        for i in range(len(field_boundary_lines)):
            field_edge = field_boundary_lines[i]
            if i < 3:
                next_field_edge = field_boundary_lines[i + 1]
            else:
                next_field_edge = field_boundary_lines[0]

            # FieldEdgeEnd = field_edge.PointAtEnd()
            # NextFieldEdgeStart = next_field_edge.PointAtStart()
            FieldBoundaryFilletSet = rg.Curve.CreateFilletCurves(field_edge.ToNurbsCurve(), field_edge.To, next_field_edge.ToNurbsCurve(),
                                                                 next_field_edge.To, corner_radius, False, True, False,
                                                                 rd.ActiveDoc.ModelAbsoluteTolerance,
                                                                 rd.ActiveDoc.ModelAbsoluteTolerance)
            # FieldFilletNum =
            field_boundary_fillet = FieldBoundaryFilletSet[-1]
            field_boundary_corners.append(field_boundary_fillet)
            # b.append(FieldBoundaryCurves[0])
            # d.append(FieldBoundaryCurves[1])
            # c.extend(field_boundary_fillet)
        field_boundary_sides = []
        for j in range(len(field_boundary_corners)):
            field_corner = field_boundary_corners[j]
            if j < 3:
                next_field_corner = field_boundary_corners[j+1]
            else:
                next_field_corner = field_boundary_corners[0]
            # FieldCornerEnd =
            field_boundary_side = rg.Line(field_corner.ToNurbsCurve().PointAtEnd, next_field_corner.ToNurbsCurve().PointAtStart).ToNurbsCurve()
            field_boundary_sides.append(field_boundary_side)
    boundary = weave(field_boundary_corners, field_boundary_sides)
    joined_boundary = rg.Curve.JoinCurves(boundary)
    return boundary, joined_boundary


def minimumsweep(safety_offset, boundary_curves):
    # minimum diagonal at corner of 2000mm
    rg.Plane.WorldXY

# The Part of the Code that Runs the Functions

FieldOutput = field(FieldLength, FieldWidth)
FieldBoundaryPolyline = FieldOutput[0]
FieldBoundarySegments = FieldOutput[1]
Output = corners(FieldBoundarySegments, FieldCornerRadius)
BoundaryCorners = Output[0]
BoundarySides = Output[1]
#         weave(FieldBoundaryCorners)
# Offset Focal Point
# if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
# if(SafetyZoneDimensions != False): #not all sports have safety zones, for example hockey
