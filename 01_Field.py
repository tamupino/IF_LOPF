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
        field_boundary_fillet_set = rg.Curve.CreateFilletCurves(field_edge.ToNurbsCurve(), field_edge.To,
                                    next_field_edge.ToNurbsCurve(), next_field_edge.To, corner_radius,
                                    False, True, False, rd.ActiveDoc.ModelAbsoluteTolerance,
                                    rd.ActiveDoc.ModelAbsoluteTolerance)
        field_boundary_fillet = field_boundary_fillet_set[-1]
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
    if boards_distance is not False:
        boards_bottom_curve = field_boundary_curve.Offset(rg.Plane.WorldXY, boards_distance,
                              rd.ActiveDoc.ModelAbsoluteTolerance, rg.CurveOffsetCornerStyle.Sharp)[0]
    else:
        boards_bottom_curve = field_boundary_polyline
    boards_vertical_vector = rg.Vector3d(0, 0, boards_height)
    boards_surface = rg.Surface.CreateExtrusion(boards_bottom_curve, boards_vertical_vector)
    xform = rg.Transform.Translation(boards_vertical_vector)
    boards_top_curve = boards_bottom_curve.Transform(xform)
    print type(boards_bottom_curve)
    return boards_surface, boards_top_curve


def focalpoint(field_boundary_polyline, focalpoint_distance, focalpoint_height):
    field_boundary_curve = field_boundary_polyline.ToNurbsCurve()
    focalpoint_offset_curve = field_boundary_curve.Offset(rg.Plane.WorldXY, -focalpoint_distance,
                       rd.ActiveDoc.ModelAbsoluteTolerance, rg.CurveOffsetCornerStyle.Sharp)[0]
    if focalpoint_height is not False:
        focalpoint_vertical_vector = rg.Vector3d(0,0, focalpoint_height)
        xform = rg.Transform.Translation(focalpoint_vertical_vector)
        focalpoint_curve = focalpoint_offset_curve.Transform(xform)
    else:
        focalpoint_curve = focalpoint_offset_curve
    return focalpoint_curve


def safetyzone(field_boundary_segments, safetyzone_end_dist, safetyzone_lat_dist):
    centre_of_field = rg.Point(WorldOrigin)
    for i in len(field_boundary_segments):
        field_boundary_segment = field_boundary_segments[i]
        field_boundary_segment_mid = rg.Point.Midpoint(field_boundary_segment)
        safetyzone_vector = rg.Vector3d(centre_of_field, field_boundary_segment_mid)
        xform = rg.Transform.Translation(safetyzone_vector)
        safetyzone_segment = field_boundary_segment.Transform(xform)
        safetyzone_segments.append(safetyzone_segment)
    return safetyzone_segments

    # for i in range(len(field_boundary_segments)):


def minimumsweep(safety_offset, boundary_curves):
    # minimum diagonal at corner of 2000mm
    rg.Plane.WorldXY

FieldLength = []
FieldWidth = []
FieldCornerRadius = []
BoardsDistance = []
BoardsHeight = []
FocalPointDistance = []
FocalPointHeight = []
SafetyZoneEnds = []
SafetyZoneLats = []

if SportType == 0:
    # Hockey
    FieldLength = 60
    FieldWidth = 30
    FieldCornerRadius = 8.5
    BoardsDistance = 0
    BoardsHeight = 1.2
    FocalPointDistance = 4
    FocalPointHeight = 0
    SafetyZoneEnds = 0
    SafetyZoneLats = 0
elif SportType == 1:
    # FIFA Football
    FieldLength = 105
    FieldWidth = 68
    FieldCornerRadius = 0
    BoardsDistance = 5
    BoardsHeight = 1
    FocalPointDistance = 0
    FocalPointHeight = 0
    SafetyZoneEnds = 10
    SafetyZoneLats = 8.5
elif SportType == 2:
    # Rugby League
    FieldLength = []
    FieldWidth = []
    FieldCornerRadius = []
    BoardsDistance = []
    BoardsHeight = []
    FocalPointDistance = []
    FocalPointHeight = []
    SafetyZoneDistance = []
elif SportType == 3:
    # Rugby Union
    FieldLength = []
    FieldWidth = []
    FieldCornerRadius = []
    BoardsDistance = []
    BoardsHeight = []
    FocalPointDistance = []
    FocalPointHeight = []
    SafetyZoneDistance = []
    # also creates a series of other options for the secondary selection

# The Part of the Code that Runs the Functions
# Create Field Boundary
FieldOutput = field(FieldLength, FieldWidth)
FieldBoundaryPolyline = FieldOutput[0]
FieldBoundarySegments = FieldOutput[1]
# if rounded corners, create rounded field corners
if FieldCornerRadius is not False:
    Output = corners(FieldBoundarySegments, FieldCornerRadius)
    BoundarySegments = Output[0]
    BoundaryJoinedCurve = Output[1]
    FieldBoundaryPolyline = BoundaryJoinedCurve
    FieldBoundarySegments = BoundarySegments
# if Offset Focal Point, create offset focal point, else take Field Boundary as focal point
if FocalPointDistance is not False:
    FocalPointOutput = focalpoint(FieldBoundaryPolyline, FocalPointDistance, FocalPointHeight)
    FocalPointCurve = FocalPointOutput[0]
# if Boards, Create Boards
if BoardsDistance is not False:
    BoardsOutput = boards(FieldBoundaryPolyline, BoardsDistance, BoardsHeight)
    BoardsSurface = BoardsOutput[0]
    BoardsTopCurve = BoardsOutput[1]

# Offset Focal Point
# if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
# if(SafetyZoneDimensions != False): #not all sports have safety zones, for example hockey
