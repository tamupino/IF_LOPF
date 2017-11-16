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
        field_boundary_side = rg.Line(field_corner.ToNurbsCurve().PointAtEnd,
                              next_field_corner.ToNurbsCurve().PointAtStart).ToNurbsCurve()
        field_boundary_sides.append(field_boundary_side)
    boundary = weave(field_boundary_corners, field_boundary_sides)
    joined_boundary = rg.Curve.JoinCurves(boundary)
    return boundary, joined_boundary


def boards(field_boundary_polyline, boards_distance, boards_height):
    field_boundary_curve = field_boundary_polyline.ToNurbsCurve()
    field_boundary_curves = []
    # for field_boundary_segment in field_boundary_polyline:
    #     field_boundary_segment.ToNurbsCurve()
    #     field_boundary_curves.append(field_boundary_segment)
    if boards_distance is not False:
        boards_bottom_curve = field_boundary_curve.Offset(rg.Plane.WorldXY, boards_distance,
                              rd.ActiveDoc.ModelAbsoluteTolerance, rg.CurveOffsetCornerStyle.Sharp)[0]
    else:
        boards_bottom_curve = field_boundary_polyline
    # boards_bottom_curve = rg.Polyline.ToNurbsCurve(field_boundary_polyline)
    boards_vertical_vector = rg.Vector3d(0, 0, boards_height)
    # boards_vertical_vector.Transform()
    boards_surface = rg.Surface.CreateExtrusion(boards_bottom_curve, boards_vertical_vector)
    # boards_top_curve = boards_bottom_curve.Transform(boards_vertical_vector)
    xform = rg.Transform.Translation(boards_vertical_vector)
    boards_top_curve = boards_bottom_curve.Transform(xform)
    print type(boards_bottom_curve)
    return boards_surface, boards_bottom_curve

def safetyzone(field_boundary_segments, safetyzone_end_dist, safetyzone_lat_dist):
    field_boundary_curves = field_boundary_segments.ToNurbsCurve()
    field_boundary_polyline = rg.Curve.JoinCurves(field_boundary_segments)

    # for i in range(len(field_boundary_segments)):


def minimumsweep(safety_offset, boundary_curves):
    # minimum diagonal at corner of 2000mm
    rg.Plane.WorldXY

FieldLength = []
FieldWidth = []

if SportType == 0
    FieldLength = 60

# The Part of the Code that Runs the Functions

FieldOutput = field(FieldLength, FieldWidth)
FieldBoundaryPolyline = FieldOutput[0]
FieldBoundarySegments = FieldOutput[1]
if FieldCornerRadius is not False:
    Output = corners(FieldBoundarySegments, FieldCornerRadius)
    BoundaryCorners = Output[0]
    BoundarySides = Output[1]
if BoardsDistance is not False:
    BoardsOutput = boards(FieldBoundaryPolyline, BoardsDistance, BoardsHeight)
    # BoardsSurface = BoardsOutput[0]
    # BoardsTopCurve = BoardsOutput[1]
#         weave(FieldBoundaryCorners)
# Offset Focal Point
# if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
# if(SafetyZoneDimensions != False): #not all sports have safety zones, for example hockey
