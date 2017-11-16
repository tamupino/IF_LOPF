from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

########################## GENERAL IMPORT STATEMENTS ##########################

# These import statements allow you to use Grasshopper's DataTree Functionality
import Grasshopper.DataTree as DataTree
import Grasshopper
import clr
clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
import Grasshopper.DataTree as DataTree
from Grasshopper.Kernel.Geometry import Node3
from Grasshopper.Kernel.Geometry import Node3List
from Grasshopper.Kernel.Geometry import Node3Proximity
import ghpythonlib.components as ghcomp
import Rhino
import System.Drawing as sd
import locale

############################### GENERAL NOTES #################################

# Lists will start with: L_
# Data Trees will start with: T_
# Paths will start with: P_
# Functions will Start with: F_
# Function Input Parameters will appear in ALL CAPS
# Variables will not have a prefix
# Comments should reference the code directly below

########################## USER DEFINED VARIABLES #############################

eye_height = 800
head_back = 0
Default_CValue = 150
Row_Max_Distance = 850

###############################################################################

""" This function takes a list of curves from rhino (these are the seat
families found in the Revit Bowl model) and finds the centerpoint of the seat.
This should be an extremely simple operation, but for some reason, the seats
coming out of Revit have a habbit of getting fucked up during export/import. """

def F_seatImportFromCurves():

    # These are all the lists defined in this function
     #These lines instantiate lists set to empty "[]"
    L_seats_correct_count = []
    L_final_seat_centroids = []
    L_seats_low_count = []
    L_seats_high_count = []
    L_seat_verts = []

    """ This is a simple check that works with the function return and prevents
    the function from crashing if it doesnt evaluate properly.  If the function
    works, we will keep the Test variable set to True. If something goes wrong and
    the function is not able to complete, the Test variable will get set to False. At
the end of the function there will be a check to determine what "Test" is set
    to.  If it's still True, the function will return the specified list. If it is
    False, the function will return nothing. """
    Test = True

    #Parse through the incoming curves (for each object in the range of the number of objects)
    for i in range (0, len(Seats)):
        myPath = GH_Path(i)

        """We want to find out how many curves are in each "Seats" object (Each seat
        should have exactly 4 curves.) First we need to test if the incoming curves
        from the "Seats" variable are actually polylines.  If they're not polylines
        we cannot break it up into sections as easily. Note: there is no operation
        included in this function that will handle non-polyline curves.  So...
        hope they're polylines
        ------------------------------------------------------------------------
        FYI: The variable assignment below could have also been written as:
        seat_crv_test = Seats[i].TryGetPolyline().  This is because "Seats[i]" is
        a curve object and the "TryGetPolyline" is method that operates on a curve.
        The "i" here represents the "i'th" object in a list.  This is not a Python
        keyword, and could really be named anything as long as it's consistent"""

        seat_crv_test = Rhino.Geometry.Curve.TryGetPolyline(Seats[i])
        #print seat_crv_test

        """The "TryGetPolyline" method asks for a curve and returns two things:
        The first item (represented by appending [0]) is a boolean determining
        whether the item passed as a polyline, and the second item ([1]) returns
        the polyline itself.  In this first IF statement we're saying: "If the
        curve is actually a polyline, get the number of segments it contains """

        if seat_crv_test[0]:
            """ The variable assignment below could have also been written as:
            seat_segments = Rhino.Geometry.Polyline.GetSegments(seat_crv_test[1]) """
            seat_segments = seat_crv_test[1].GetSegments()

            if len(seat_segments) == 4:
                #This puts all the seats that do not need to be modified on a list
                L_seats_correct_count.append(Seats[i])
                #This calculates the centroids of the seats and puts them on a
                #final list of points that will be sorted later
                L_final_seat_centroids.append(Rhino.Geometry.AreaMassProperties.Compute(Seats[i]).Centroid)

            elif len(seat_segments) < 4:
                # This puts all the seats with lower than expected vertices into a list
                # Currently, no actions have been written to deal with this condition.
                L_seats_low_count.append(Seats[i])

            elif len(seat_segments) > 4:
                """This puts all the seats with greater than expected vertices into a list
                It's moderately useful to have all the seat curves together in a list, but
                what's really important is the centroids of the seats.  Since the broken
                seat curves have no centroids, the next few operations will generate them in
                a series of steps, and then add them to the list of the existing centroids """
                L_seats_high_count.append(Seats[i])
                """This line creates a list of lists. According to the rhinocommon documentation
                a polyline is really just a list of points, so using the "list()" operation
                and setting it == to a new list ends up creating a list of lists.  If you
                try to visualize this in the GH output you will get an error because the list
                still needs to be translated into something GH understands - i.e. a branched
                path of points. If needed, this can be done by iterating through the points in
                "L_seat_verts" and adding them to a path that you've created."""
                L_seat_verts = list(seat_crv_test[1])

                """ The next step is to construct a new centroid for the seats that
                failed the test. To do this we will isolate the midpoints of the
                curve segments that represent the "front" of the seat and move that
                point to the correct centroid location.  In order to get these directions
                relative to the INDIVIDUAL orientation of each seat, we will create
                a coordinate system for each group of bad seats and pull off the required
                vectors"""

                """ We will build the remapping plane from an origin point and two vectors.
                The origin is the first point in the polyline object and the two
                vectors will be pulled from the start/end points of two of the seats edges
                The next few variables are not lists because for every seat we need
                one corresponding property"""
                remap_plane_originPt = L_seat_verts[0]

                """When you subtract a point from a point you get a vector. We need both vectors to
                create the plane, but only need one to define which way the point needs to move
                to create the new centroid."""
                remap_plane_vect1 = (Rhino.Geometry.Vector3d(L_seat_verts[0]-L_seat_verts[1]))

                """This vector starts at the beginning of the polyline and wants the last point in the
                group. Normally that would be index [-1] but in this case there is a start and an
                end to the polylines and they occupy the same place in space. therefore: [-2] """
                remap_plane_vect2 = (Rhino.Geometry.Vector3d(L_seat_verts[0]-L_seat_verts[-2]))

                # This creates the new coordinate plane for each seat object
                remap_plane = Rhino.Geometry.Plane(remap_plane_originPt,remap_plane_vect1,remap_plane_vect2)

                """Eventually we want to sort these physical seat curve midpoints
                by their locations relative to the Y value of the remapped plane.
                This will tell us which midpoints are at the front of the seat.
                We can then isolate those points and move them back to where the centroid should/would be. """

                # These new lists will be used to collect the information off of the seat segments
                L_seat_segment_midpoint = []
                L_remapped_midpoints_YValues = []
                L_seat_curve_lengths = []

                #This loop goes through each line in the seat objects:
                for line in seat_segments:
                    # In RhinoCommon, line objects always have a 0:1 domain, so finding the midpoint is
                    # as simple as picking a the .5 as a curver parameter value
                    seat_segment_midpoint = line.PointAt(.5)

                    #This line is appending the above created midpoints to a collective list above
                    L_seat_segment_midpoint.append(seat_segment_midpoint)

                    """A new midpoint with coordinates relative to "remap_plane" object
                    is built using the original seat segment as an input.  We're not making this
                    a list, and are just keeping it as a variable because we dont actually need the

                    #remapped_midpoint object.  We need the Y value of that point in a separate list. """
                    remapped_midpoint = remap_plane.RemapToPlaneSpace(seat_segment_midpoint)[1]

                    # This adds all those Y values to the list created before the for loop
                    L_remapped_midpoints_YValues.append(remapped_midpoint.Y)

                    """One last step here, we're getting a list of curve lengths for all segments because
                    to create the final cenroid locations, we're going to move the midpoints
                    by 1/2 of the length of the shorter set of segments """
                    L_seat_curve_lengths.append(line.Length)

                """This is the actual sorting operation. The "L_segment_midpoints" are
                sorted according to the relative Y position in the "remap_plane"s
                http://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list"""
                L_sorted_midpoints = [x for (y,x) in sorted(zip(L_remapped_midpoints_YValues,L_seat_segment_midpoint))]

                """After the midpoints have been sorted, the list below is created. It
                takes the "L_sorted_midpoints" list and pulls off just the points that
                are on the front of the seat. Below, the square brackets
                at the end of "L_sorted_midpoints" is indicating the list index that we
                want to pull out.  [x:x] formatting requires you to specify a start
                and stop location for the index.  Because a broken seat "object" can contain
                more than one actual seat, the points need to be evaluated before they can be selected.
                Since we already know that our "L_seats_high_count" will contain curves in
                groups of 4, we can divide the number of edges in each group by 4 to figure
                out how many points each sublist should contain."""
                L_sorted_frontpoints = L_sorted_midpoints[0:int(len(seat_segments)/4)]


                """The last step here is to move the end points to the center of the seats
                and then add them back into the final list of center points.  The loop
                below goes through each"""
                for j in range (0, len(L_sorted_frontpoints)):
                    L_sorted_frontpoints[j] += remap_plane.YAxis * (L_seat_curve_lengths[1]/2)
                    L_final_seat_centroids.append(L_sorted_frontpoints[j])
                    # If the code makes it this far it will jump directly to the last"if Test: statement

            else:
                print "Seats not able to be processed at this time"

                # the "Test" variable was initially set to True at the beinning of the function
                # Setting it to false allows us to define what happens when the first test fails
                Test = False

                # This exits the current loop and kicks you out to one indent before
                break

    # "If Test" is shorthand for "if Test = True".  If the Test variable has managed to stay
    # the total function return will be the complete (Yet Unsorted) list of seat centerpoints
    if Test:
        return L_final_seat_centroids

    # If a failure point triggers a False anywhere the function will return nothing
    # ... which is better than crashing.
    else:
        return None


""" This function takes a list of unsorted centerpoints and turns them into branched
lists based on point proximity.  This is direct copy of the grasshopper component
"Point Groups" and was decompiled in ilSpy (http://ilspy.net/) and directly ported to python.
Hence the lack of documentation """

def F_groupPoints(PTS_TO_GROUP, DISTANCE):

    nodeList1 = Grasshopper.Kernel.Geometry.Node3List()
    nodeList2 = Grasshopper.Kernel.Geometry.Node3List()

    for i in range(0, len(PTS_TO_GROUP)):
        if PTS_TO_GROUP[i] != None:
            if PTS_TO_GROUP[i].IsValid:
                node = Node3(PTS_TO_GROUP[i], i)
                nodeList1.Append(node)
                nodeList2.Append(node)

    nodeTree = nodeList1.CreateTree(0.1, False, 25)
    limit = 0
    list2 = []

    while nodeList2.Count > 0:
        nodeList3 = Node3List()
        list2.append(nodeList3)
        nodeList4 = Node3List()
        num4 = nodeList2.Count - 1
        node2 = nodeList2[num4]
        nodeList3.Append(node2)
        nodeList4.Append(node2)
        nodeList2.RemoveAt(num4)
        nodeTree.Root.RemoveNode(nodeList1, node2)
        limit += 1
        if nodeList2.Count == 0:
            break
        while True:
            nodeList5 = Node3List()
            for i in range(0, nodeList4.Count):
                nodeProximity = Node3Proximity(nodeList4[i], -1, nodeList1.Count, 0.0, DISTANCE)
                nodeTree.SolveProximity(nodeProximity)
                if nodeProximity.CurrentCount != 0:
                    list3 = nodeProximity.IndexList
                    for j in range(len(list3)-1, -1, -1):
                        node = nodeList1[list3[j]]
                        nodeList2.Remove(node)
                        nodeTree.Root.RemoveNode(nodeList1, node)
                        nodeList5.Append(node)
                        nodeList3.Append(node)
                    if nodeList1.Count == 0:
                        break
            if nodeList1.Count == 0 or nodeList5.Count == 0:
                break
            nodeList4.Clear()
            nodeList4.AppendRange(nodeList5.InternalList)
            if limit > 25:
                nodeTree.Root.TrimExcess()
                limit = 0

    pointTree = DataTree[Rhino.Geometry.Point3d]()
    indexTree = DataTree[int]()
    for i in range(0, len(list2)):
        ghPath = Grasshopper.Kernel.Data.GH_Path(i)
        list4 = []
        list5 = []
        nodeList6 = list2[i]
        for j in range(0, nodeList6.Count):
            ptList = list4
            point = Rhino.Geometry.Point3d(nodeList6[j].x, nodeList6[j].y, nodeList6.Node[j].z)
            ptList.append(point)
            list5.Add(nodeList6[j].tag)
        pointTree.AddRange(list4, ghPath)
        indexTree.AddRange(list5, ghPath)
    return [pointTree, indexTree]

"""This function takes points in a data tree and sorts them out by rows """

def F_sortSeatsByRow(T_POINTS):
    # At a later time, add code here to warn user that data must be in a branched format
    # or build a method to handle a flat, list input.

    #This creates the DataTree we will be adding our finished rows to
    T_SortByRows = DataTree[Rhino.Geometry.Point3d]()

    """ For each section of seating we want to sort by rows. The previous "F_groupPoints"
    function created one branch of data per section, so we want to iterated through
    each section one by one and perform a sort operation.  The ".Branchcount" will
    give us the number of sections.  We're then creating a variable that is equal to
    all the points in a section with "section_pt_group".  The ".Brances[i]" phrase again
    represents an individual section at the i'th position.
            In the Loop below:
            i = Sections
            j = Rows
            pt = the point iterator in the groups of points that represent the sections"""

    for i in range (0, T_POINTS.BranchCount):
        section_pt_group = T_POINTS.Branches[i]
        #This is an empty list we're creating to store the unique values of each row
        L_unique_ZVal = []

        """ We've isolated a section of seating and the "pt" loop now represents us iterating
        through each seat in the group one by one.  """

        for pt in section_pt_group:

            """ Each row in a section should have the same Z value, therefore we can
            identify the number of rows in a section by looking at how many unique values
            of Z are present in the collection.  The variable "isUnique" will be responsible
            for deciding what to do with each value we run into. If it is True, the
            number will be added to the (currently empty) list of unique Zvalues that
            we created above. If it is False, the program will just skip to the next
            point for evaluation. """
            isUnique = True
            for zval in L_unique_ZVal:
                # all the rows should be at the same elevation, but sometimes modeling
                # inacuracies can cause this to be a bit off.  Currently, 2mm is the
                # threshold for what determines a new row, but that should be evaluated
                # for each project and adjusted as necessary
                if abs(int(pt.Z) - zval) < 2:
                    isUnique = False
                    break
            if isUnique:
                L_unique_ZVal.append(int(pt.Z))
        L_unique_ZVal.sort()
        #print L_unique_ZVal


        for pt in section_pt_group:
            for j in range (0, len(L_unique_ZVal)):
                if abs(int(pt.Z) - L_unique_ZVal[j]) < 2:
                    P_Sorted_by_rows = GH_Path(i,j)
                    T_SortByRows.Add(pt,P_Sorted_by_rows)
        #print len(L_unique_ZVal)
    return T_SortByRows

""" This function calculates the C-Value for every seat """

def CValue_Calc(SORTED_ROWS):

    cvalue_D = 0 #Found
    cvalue_T = 0 #Found
    cvalue_N = 0 #Foundaaaaaaaaaaaaa
    cvalue_R = 0 #Found
    CValue_Final = 0

    L_CValue_List = []

    T_SightLines = DataTree[Rhino.Geometry.Line]()
    T_Seats = DataTree[Rhino.Geometry.Point3d]()
    T_EyePoints = DataTree[Rhino.Geometry.Point3d]()
    T_RowCurves = DataTree[Rhino.Geometry.NurbsCurve]()
    T_TPoints = DataTree[Rhino.Geometry.Point3d]()
    T_CValue = DataTree[float]()
    T_CurveBelow = DataTree[Rhino.Geometry.NurbsCurve]()

    SortCircle = Rhino.Geometry.Circle(Rhino.Geometry.Plane.WorldXY,300)

    for i in range (0,SORTED_ROWS.BranchCount):
        List = []
        SortList = []

        for j in range(0,len(SORTED_ROWS.Branches[i])):
            P_Sorted_by_rows = SORTED_ROWS.Paths[i]
            #print len(P_Sorted_by_rows)
            Seat = (SORTED_ROWS.Branches[i])[j]
            tparam = Rhino.Geometry.Curve.ClosestPoint(PitchBoundary,Seat)[1]
            tpoint = Rhino.Geometry.Curve.PointAt(PitchBoundary,tparam)
            eye_pt = Seat + Rhino.Geometry.Vector3d(0,0,eye_height)
            sightline = Rhino.Geometry.Line(eye_pt,tpoint)
            List.append(Seat)
            #SortList = Rhino.Geometry.Point3d.SortAndCullPointList(List,50)

            T_SightLines.Add(sightline,P_Sorted_by_rows)
            T_EyePoints.Add(eye_pt,P_Sorted_by_rows)
            T_Seats.Add(Seat,P_Sorted_by_rows)
            T_TPoints.Add(tpoint,P_Sorted_by_rows)

        SortList = ghcomp.SortAlongCurve(List,SortCircle)[0]

        if type(SortList) is Rhino.Geometry.Point3d:
            linecurve = Rhino.Geometry.Line(SortList, (SortList + Rhino.Geometry.Vector3d(0,0,50)))
            curve = linecurve.ToNurbsCurve()

        elif len(SortList) == 2:
            linecurve = Rhino.Geometry.Line(SortList[0],SortList[1])
            curve = linecurve.ToNurbsCurve()

        elif len(SortList) == 3:
            plinecurve = Rhino.Geometry.Polyline(SortList)
            curve = plinecurve.ToNurbsCurve()

        elif len(SortList) > 3:
            curve = Rhino.Geometry.NurbsCurve.Create(False,3,SortList)

        T_RowCurves.Add(curve,P_Sorted_by_rows)


    for i in range (0,SORTED_ROWS.BranchCount):

        P_Sorted_by_rows = SORTED_ROWS.Paths[i]

        if P_Sorted_by_rows.Indices[1] == 0:
            for j in range(0,len(SORTED_ROWS.Branches[i])):
                CValue_Final = Default_CValue
                T_CValue.Add(CValue_Final,P_Sorted_by_rows)
                L_CValue_List.append(CValue_Final)

        else:
            for j in range(0,len(SORTED_ROWS.Branches[i])):
                pass

                #print T_RowCurves.Branches[i][0]
                curve_current = T_RowCurves.Branches[i][0].Duplicate()
                curve_below = T_RowCurves.Branches[i-1][0].Duplicate()

                curve_currrent_endpt = curve_current.PointAtEnd
                curve_below_endpt = curve_below.PointAtEnd

                dif_btwn_crvs = (curve_current.GetLength()) - (curve_below.GetLength())
                curve_below.Extend(dif_btwn_crvs,dif_btwn_crvs)
                curve_below.Translate(0,0,(curve_currrent_endpt.Z - curve_below_endpt.Z))
                seat = T_Seats.Branches[i][j]
                ParamOnMovedCurve = Rhino.Geometry.Curve.ClosestPoint(curve_below,seat)[1]
                PointOnMovedCurve = Rhino.Geometry.Curve.PointAt(curve_below,ParamOnMovedCurve)

                #if seat.DistanceTo(PointOnMovedCurve) <

                cvalue_T = seat.DistanceTo(PointOnMovedCurve)

                if Override: # If error test = "True" Override the bad values
                    if cvalue_T >= Row_Max_Distance:
                        cvalue_T = Row_Max_Distance
                    else:
                        cvalue_T = seat.DistanceTo(PointOnMovedCurve)
                else: #if error test = "False"
                    cvalue_T = seat.DistanceTo(PointOnMovedCurve)


                cvalue_N = curve_currrent_endpt.Z - curve_below_endpt.Z
                cvalue_R = (T_EyePoints.Branches[i][j].Z-T_TPoints.Branches[i][j].Z)
                cvalue_D = Rhino.Geometry.Point3d.DistanceTo(T_EyePoints.Branches[i][j], (T_TPoints.Branches[i][j] + Rhino.Geometry.Vector3d(0,0,cvalue_R)))

                CValue_Final = int((cvalue_D *(cvalue_N+cvalue_R) / (cvalue_D + cvalue_T) ) - cvalue_R)

                #if the distance between a seat and the next closest seat (at a lower elevation) is greater than X then we want to set the cvalue to the default.
                #print type(SORTED_ROWS.Branches[i][j])



                L_CValue_List.append(CValue_Final)
                T_CValue.Add(CValue_Final,P_Sorted_by_rows)

                T_CurveBelow.Add(curve_below,P_Sorted_by_rows)


    return [T_SightLines,T_EyePoints,T_RowCurves,T_Seats,T_CValue,L_CValue_List,T_CurveBelow]

""" This function visualizes the output of the C-Value Calculation """

def Vis_Output(C_VALUES, EYE_LOCATIONS):

    T_Spheres = DataTree[Rhino.Geometry.Sphere]()
    T_Colors = DataTree[sd.Color]()

    for i in range (0, C_VALUES.BranchCount):
        P_Sorted_by_rows = C_VALUES.Paths[i]
        for j in range (0, len(EYE_LOCATIONS.Branches[i])):
            VizPt = Rhino.Geometry.Sphere(EYE_LOCATIONS.Branches[i][j],200)
            T_Spheres.Add(VizPt,P_Sorted_by_rows)

            # 0-60 = Black
            if C_VALUES.Branches[i][j] >= 0 and C_VALUES.Branches[i][j] < 60:
                SphereColors = sd.Color.FromArgb(20,20,20)

            # 60-70 = Red
            elif C_VALUES.Branches[i][j] >= 60 and C_VALUES.Branches[i][j] <= 70:
                SphereColors = sd.Color.FromArgb(255,0,0)

            # 70-90 = Orange
            elif C_VALUES.Branches[i][j] >70 and C_VALUES.Branches[i][j] < 90:
                SphereColors = sd.Color.FromArgb(255,165,0)

            # 90-120 = Yellow
            elif C_VALUES.Branches[i][j] >= 90 and C_VALUES.Branches[i][j] <= 120:
                SphereColors = sd.Color.FromArgb(255,255,0)

            # 120-150 = Green
            elif C_VALUES.Branches[i][j] >120 and C_VALUES.Branches[i][j] <=150:
                SphereColors = sd.Color.FromArgb(0,128,0)

            # > 150 = Lime
            elif C_VALUES.Branches[i][j] >150:
                SphereColors = sd.Color.FromArgb(0,255,0)

            # Everything Else = Magenta
            else:
                SphereColors = sd.Color.FromArgb(255,0,255)

            T_Colors.Add(SphereColors,P_Sorted_by_rows)

    return [T_Spheres,T_Colors]

def percentages(C_VALUE_LIST):

    locale.setlocale(locale.LC_ALL, 'en_US')

    L_GT_120 = []
    L_BT_90_120 = []
    L_BT_70_90 = []
    L_BT_60_70 = []
    L_BT_0_60 = []
    L_ERROR = []


    for i in C_VALUE_LIST:

        if i >= 120:
            L_GT_120.append(i)
        elif i > 90 and i < 120:
            L_BT_90_120.append(i)
        elif i >= 70 and i <= 90:
            L_BT_70_90.append(i)
        elif i > 60 and i < 70:
            L_BT_60_70.append(i)
        elif i > 0 and i <= 60:
            L_BT_0_60.append(i)
        elif i < 0:
            L_ERROR.append(i)


    GT_120 =      100.0 * (float(len(L_GT_120)) / float(len(C_VALUE_LIST)))
    BT_90_120 =   100.0 * (float(len(L_BT_90_120))/ float(len(C_VALUE_LIST)))
    BT_70_90 =    100.0 * (float(len(L_BT_70_90)) / float(len(C_VALUE_LIST)))
    BT_60_70 =    100.0 * (float(len(L_BT_60_70)) / float(len(C_VALUE_LIST)))
    LT_0_60 =     100.0 * (float(len(L_BT_0_60)) / float(len(C_VALUE_LIST)))
    ERROR =       100.0 * (float(len(L_ERROR)) / float(len(C_VALUE_LIST)))


    v1 = "C-Value Percentages:"
    v1 += "\n"
    v1 += "\nTotal Seats: " + locale.format("%d", (len(L_GT_120) + len(L_BT_90_120) + len(L_BT_70_90) + len(L_BT_60_70) + len(L_BT_0_60) + len(L_ERROR)), grouping=True)
    v1 += "\n"
    v1 += "\nGreater than C120:       " + "{0:.1f}%".format(GT_120) + "  (" + str(len(L_GT_120)) + " Seats - Color: Green)"
    v1 += "\nBetween C90 and C120:    " + "{0:.1f}%".format(BT_90_120) + "  (" + str(len(L_BT_90_120)) + " Seats - Color: Yellow)"
    v1 += "\nBetween C70 and C90:     " + "{0:.1f}%".format(BT_70_90) + "  (" + str(len(L_BT_70_90)) + " Seats - Color: Orange)"
    v1 += "\nBetween C60 and C70:      " + "{0:.1f}%".format(BT_60_70) + "  (" + str(len(L_BT_60_70)) + "  Seats - Color: Red)"
    v1 += "\nBetween C0  and C60:      " + "{0:.1f}%".format(LT_0_60) + "  (" + str(len(L_BT_0_60)) + "   Seats - Color: Black)"
    v1 += "\nModeling Errors:          " + "{0:.1f}%".format(ERROR) + "  (" + str(len(L_ERROR)) + "   Seats - Color: Magenta)"
    v1 += "\n"
    v1 += "\n------------------------------------------------------------"
    v1 += "\n"
    v1 += "\nPass/Fail (At C90):"
    v1 += "\nPass: " + "{0:.1f}%".format(GT_120 + BT_90_120) + "  (" + str(len(L_GT_120) + len(L_BT_90_120)) + " Seats)"
    v1 += "\nFail: " + "{0:.1f}%".format(ERROR + LT_0_60 + BT_60_70 + BT_70_90) + "  (" + str(len(L_ERROR) + len(L_BT_0_60) + len(L_BT_60_70) + len(L_BT_70_90)) + " Seats)"
    v1 += "\n"
    v1 += "\n------------------------------------------------------------"
    v1 += "\n"
    v1 += "\nPass/Fail (At C70):"
    v1 += "\nPass: " + "{0:.1f}%".format(GT_120 + BT_90_120 + BT_70_90) + "  (" + str(len(L_GT_120) + len(L_BT_90_120) + len(L_BT_70_90)) + " Seats)"
    v1 += "\nFail:  " + "{0:.1f}%".format(ERROR + LT_0_60 + BT_60_70) + "  (" + str(len(L_ERROR) + len(L_BT_0_60) + len(L_BT_60_70)) + " Seats)"
    v1 += "\n"
    v1 += "\n------------------------------------------------------------"
    v1 += "\n"
    v1 += "\nPass/Fail (At C60):"
    v1 += "\nPass: " + "{0:.1f}%".format(GT_120 + BT_90_120 + BT_70_90 + BT_60_70) + "  (" + str(len(L_GT_120) + len(L_BT_90_120) + len(L_BT_70_90) + len(L_BT_60_70)) + " Seats)"
    v1 += "\nFail:  " + "{0:.1f}%".format(ERROR + LT_0_60) + "  (" + str(len(L_ERROR) + len(L_BT_0_60)) + " Seats)"

    return v1


############################# RUN THE CALCULATIONS #############################

ptGroups = (F_groupPoints(F_seatImportFromCurves(), 1200))[0]

seat_centroids = F_seatImportFromCurves()

ptRows = F_sortSeatsByRow(ptGroups)


CValue_Calc(ptRows)
Sight_lines = CValue_Calc(ptRows)[0]
Eye_Points = CValue_Calc(ptRows)[1]
Row_Curves = CValue_Calc(ptRows)[2]
CValue = CValue_Calc(ptRows)[4]
CValue_List = CValue_Calc(ptRows)[5]
Curve_Below = CValue_Calc(ptRows)[6]


Vis_Output(CValue,Eye_Points)
Spheres = Vis_Output(CValue,Eye_Points)[0]
Colors = Vis_Output(CValue,Eye_Points)[1]


Totals = percentages(CValue_List)
