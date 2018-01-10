import Rhino.Geometry as rg
import math
import Rhino.RhinoDoc as rd
import System
import collections

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


def corners(field_boundary_input, corner_radius):
    print "Corners Works"
    field_boundary_corners = []
    if isinstance(field_boundary_input, rg.Rectangle3d):
        field_boundary_lines = field_boundary_input.ToNurbsCurve().DuplicateSegments()
    else:
        field_boundary_lines = field_boundary_input
    for i in range(len(field_boundary_lines)):
        field_edge = field_boundary_lines[i]
        if i < 3:
            next_field_edge = field_boundary_lines[i + 1]
        else:
            next_field_edge = field_boundary_lines[0]
        if isinstance(next_field_edge, rg.Curve) != True:
            next_field_edge = next_field_edge.ToNurbsCurve()
        if isinstance(field_edge, rg.Curve) != True:
            field_edge = field_edge.ToNurbsCurve()
        field_boundary_fillet_set = rg.Curve.CreateFilletCurves(field_edge, field_edge.PointAtEnd,
                                    next_field_edge, next_field_edge.PointAtEnd, corner_radius,
                                    False, True, False, rd.ActiveDoc.ModelAbsoluteTolerance,
                                    rd.ActiveDoc.ModelAbsoluteTolerance)
        for i in range( 0, len(field_boundary_fillet_set)):
            if isinstance(field_boundary_fillet_set[i], rg.ArcCurve):
                field_boundary_fillet = field_boundary_fillet_set[i]
                break
        field_boundary_corners.append(field_boundary_fillet)
    field_boundary_sides = []
    for i in range(len(field_boundary_corners)):
        field_corner = field_boundary_corners[i]
        if i < 3:
            next_field_corner = field_boundary_corners[i+1]
        else:
            next_field_corner = field_boundary_corners[0]
        field_boundary_side = rg.Line(field_corner.ToNurbsCurve().PointAtEnd,
                              next_field_corner.ToNurbsCurve().PointAtStart).ToNurbsCurve()
        field_boundary_sides.append(field_boundary_side)
    boundary = weave(field_boundary_corners, field_boundary_sides)
    joined_boundary = rg.Curve.JoinCurves(boundary)
    if isinstance(joined_boundary, System.Array[rg.Curve]):
        joined_boundary = joined_boundary[0]
    return boundary, joined_boundary


def offset(original_curve, offset_distance):
    print "Offset Works"
    if isinstance(original_curve, collections.Sequence):
        original_curve = original_curve[0]
    if isinstance(original_curve, rg.Curve):
        field_boundary_curve = original_curve
        print "Option 1"
    elif isinstance(original_curve, rg.Rectangle3d):
        field_boundary_curve = original_curve.ToNurbsCurve()
        print "Option 2"
    else:
        field_boundary_curve = original_curve.ToNurbsCurve()
        print "Option 3"
    focalpoint_offset_curve = field_boundary_curve.Offset(rg.Plane.WorldXY, -offset_distance,
                                                          rd.ActiveDoc.ModelAbsoluteTolerance,
                                                          rg.CurveOffsetCornerStyle.Sharp)[0]
    return focalpoint_offset_curve


# Process Functions


def field(field_length, field_width):
    field_width_interval = rg.Interval(-0.5*field_width, 0.5*field_width)
    field_length_interval = rg.Interval(-0.5*field_length, 0.5*field_length)
    field_boundary = rg.Rectangle3d(rg.Plane.WorldXY, field_width_interval, field_length_interval).ToPolyline()
    field_boundary_lines = field_boundary.GetSegments()
    return field_boundary, field_boundary_lines


def boards(field_boundary_polyline, boards_distance, boards_height):
    print "Boards Works"
    field_boundary_curve = field_boundary_polyline.ToNurbsCurve()
    if boards_distance != 0:
        boards_bottom_curve = field_boundary_curve.Offset(rg.Plane.WorldXY, boards_distance,
                              rd.ActiveDoc.ModelAbsoluteTolerance, rg.CurveOffsetCornerStyle.Sharp)[0]
    else:
        boards_bottom_curve = field_boundary_polyline
    boards_vertical_vector = rg.Vector3d(0, 0, boards_height)
    boards_surface = rg.Surface.CreateExtrusion(boards_bottom_curve, boards_vertical_vector)
    xform = rg.Transform.Translation(boards_vertical_vector)
    boards_top_curve = boards_bottom_curve.Transform(xform)
    return boards_surface, boards_top_curve


def focalpoint(field_boundary_polyline, focalpoint_distance, focalpoint_height):
    focalpoint_offset_curve = offset(field_boundary_polyline, focalpoint_distance)
    if focalpoint_height != 0:
        focalpoint_vertical_vector = rg.Vector3d(0, 0, focalpoint_height)
        xform = rg.Transform.Translation(focalpoint_vertical_vector)
        focalpoint_curve = focalpoint_offset_curve.Transform(xform)
    else:
        focalpoint_curve = focalpoint_offset_curve
    return focalpoint_curve


def safetyzone(field_boundary_segments, safetyzone_end_dist, safetyzone_lat_dist):
    safetyzone_segments = []
    centre_of_field = rg.Point3d.Origin
    for field_boundary_segment in field_boundary_segments:
        # field_boundary_segment = field_boundary_segments[i]
        field_boundary_segment_mid = field_boundary_segment.PointAt(0.5)
        safetyzone_vector = rg.Vector3d(field_boundary_segment_mid - centre_of_field)
        safetyzone_vector.Unitize()
        if safetyzone_vector.X != 0:
            lat_vector = safetyzone_lat_dist * safetyzone_vector
            lat_xform = rg.Transform.Translation(lat_vector)
            safetyzone_segment = field_boundary_segment.Transform(lat_xform)
        elif safetyzone_vector.Y != 0:
            end_vector = safetyzone_end_dist * safetyzone_vector
            end_xform = rg.Transform.Translation(end_vector)
            safetyzone_segment = field_boundary_segment.Transform(end_xform)
        # xform = rg.Transform.Translation(safetyzone_vector)
        safetyzone_segments.append(field_boundary_segment)
    corner_gaps = safetyzone_segments[0].To.DistanceTo(safetyzone_segments[1].From)
    if corner_gaps > 0:
        extend_corners = []
        for i in range(len(safetyzone_segments)):
            safetyzone_edge = safetyzone_segments[i]
            if i < 3:
                next_safetyzone_edge = safetyzone_segments[i + 1]
            else:
                next_safetyzone_edge = safetyzone_segments[0]
            safetyzone_fillet_set = rg.Curve.CreateFilletCurves(safetyzone_edge.ToNurbsCurve(), safetyzone_edge.To,
                                    next_safetyzone_edge.ToNurbsCurve(), next_safetyzone_edge.To, 0,
                                    False, True, True, rd.ActiveDoc.ModelAbsoluteTolerance,
                                    rd.ActiveDoc.ModelAbsoluteTolerance)
            safetyzone_fillet_set_end = safetyzone_fillet_set[0].PointAtEnd
            # for i in range(0, len(safetyzone_fillet_set)):
            #     if isinstance(safetyzone_fillet_set[i], rg.Line):
            #         safetyzone_fillet = safetyzone_fillet_set[i]
            #         break
            #         extend_corners.append(safetyzone_fillet[0])
            extend_corners.append(safetyzone_fillet_set_end)
        safetyzone_rect = rg.Rectangle3d(rg.Plane.WorldXY,extend_corners[0], extend_corners[2])
    return safetyzone_rect


def perpframes(input_list):
    section_frames = []
    for i in range(len(input_list)):
        input_item = input_list[i]
        input_item.Domain = rg.Interval(0, 1)
        section_frame = input_item.PerpendicularFrameAt(0.0)[1]
        print type(section_frame)
        section_frames.append(section_frame)
    return section_frames


# def sectionframes(boundary_curves):
#     minimum_zone_offset = 0.75
#     minimum_offset_radius = minimum_zone_offset * math.pi
#     safetyzone_offset_curve = offset(boundary_curves, minimum_zone_offset)
#     corners_output = corners(safetyzone_offset_curve, minimum_offset_radius)
#     BoundarySegments = corners_output[0]
#     BoundaryJoinedCurve = corners_output[1]


# Simplify Curve


# List of Enums

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
    # EUFA Football
    FieldLength = 105
    FieldWidth = 68
    FieldCornerRadius = 0
    BoardsDistance = 4
    BoardsHeight = 1
    FocalPointDistance = 0
    FocalPointHeight = 0
    SafetyZoneEnds = 10
    SafetyZoneLats = 8.5
elif SportType == 3:
    # Rugby League
    FieldLength = None
    FieldWidth = None
    FieldCornerRadius = None
    BoardsDistance = None
    BoardsHeight = None
    FocalPointDistance = None
    FocalPointHeight = None
    SafetyZoneDistance = None
elif SportType == 4:
    # Rugby Union
    FieldLength = None
    FieldWidth = None
    FieldCornerRadius = None
    BoardsDistance = None
    BoardsHeight = None
    FocalPointDistance = None
    FocalPointHeight = None
    SafetyZoneDistance = None
elif SportType == 5:
    # Basketball
    FieldLength = None
    FieldWidth = None
    FieldCornerRadius = None
    BoardsDistance = None
    BoardsHeight = None
    FocalPointDistance = None
    FocalPointHeight = None
    SafetyZoneDistance = None
elif SportType == 6:
    # American Football
    FieldLength = None
    FieldWidth = None
    FieldCornerRadius = None
    BoardsDistance = None
    BoardsHeight = None
    FocalPointDistance = None
    FocalPointHeight = None
    SafetyZoneDistance = None
    # also creates a series of other options for the secondary selection

# The Part of the Code that Runs the Functions
# Create Field Boundary
FieldOutput = field(FieldLength, FieldWidth)
FieldBoundaryPolyline = FieldOutput[0]
FieldBoundarySegments = FieldOutput[1]
# if rounded corners, create rounded field corners
if FieldCornerRadius != 0:
    Output = corners(FieldBoundarySegments, FieldCornerRadius)
    BoundarySegments = Output[0]
    BoundaryJoinedCurve = Output[1]
    FieldBoundaryPolyline = BoundaryJoinedCurve
    FieldBoundarySegments = BoundarySegments
# if Offset Focal Point, create offset focal point, else take Field Boundary as focal point
if FocalPointDistance != 0:
    FocalPointOutput = focalpoint(FieldBoundaryPolyline, FocalPointDistance, FocalPointHeight)

    # FocalPointCurve = FocalPointOutput[0]
# if Boards, Create Boards
if BoardsHeight != 0:
    BoardsOutput = boards(FieldBoundaryPolyline, BoardsDistance, BoardsHeight)
    BoardsSurface = BoardsOutput[0]
    BoardsTopCurve = BoardsOutput[1]

# Offset Focal Point
# if(FocalOffsetDistance != False):
#    FocalOffset = rg.Curve.Offset(rg.Plane.WorldXY, FocalOffsetDistance, )
# Build Boundary Area
if SafetyZoneEnds != False:  #not all sports have safety zones, for example hockey
    SafetyZoneOutput = safetyzone(FieldBoundarySegments, SafetyZoneEnds, SafetyZoneLats)
    RawSeatingCurve = SafetyZoneOutput
else:
    RawSeatingCurve = FieldBoundaryPolyline
# Default minimum sweep curve, to derive perp frames
minimum_zone_offset = 0.75
minimum_offset_radius = minimum_zone_offset * math.pi
# SeatingOriginCurve = offset(RawSeatingCurve, minimum_zone_offset)
# SeatingOriginCurves = rg.PolyCurve.Explode(SeatingOriginCurve)
if FieldCornerRadius == 0:
    corners_output = corners(RawSeatingCurve, minimum_offset_radius)
    BoundarySegments = corners_output[0]
    BoundaryJoinedCurve = corners_output[1]
else:
    BoundarySegments = RawSeatingCurve.DuplicateSegments()
SectionFrames = perpframes(BoundarySegments)
