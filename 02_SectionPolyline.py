# Import typical rhinoscript stuff
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino.Geometry as rg

# Import stuff needed for multithreading
import System.Collections.Generic as scg
import System.Threading.Tasks as tasks

# These are for accessing GH classes
import clr

clr.AddReference("Grasshopper")
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


# Calculate_Profile
# This function will calculate the point locations at the back of each tread
# where the seat attaches. It returns a list of points which is needed by
# the Draw_Pline function.
def Calculate_Profile(o_plane, start_point, number_rows, start_distance, tread_elevation, tread_size, max_riser,
                      min_increment, eye_level, sight_clearance, riser_thickness, tread_thickness):
    # Define the variables for this function
    delta_x = start_point.X
    delta_y = start_point.Y
    row = 1
    clear_flag = 0
    clear_row = 0
    x = start_distance + delta_x
    y = tread_elevation + delta_y
    eye_offset = 0
    tread_height_list = []
    tread_depth_list = []
    deck_cvalues = []
    profile_list = []
    Xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, o_plane)
    profile_origin = rg.Point3d(x,y,0) #type: rg.Point3d
    profile_origin.Transform(Xform)
    profile_list.append(profile_origin)

    while row < number_rows:
        # Calculate the first riser
        # New formula with eye offset
        ideal_riser = ((((y + eye_level + sight_clearance) / (x - eye_offset)) *
                      (x + tread_size - eye_offset)) - (y + eye_level))
        print "Ideal Riser Value:" + str(ideal_riser)
        riser = min_increment * int((ideal_riser / min_increment)) + min_increment

        if riser > max_riser:
            riser = max_riser
        print "Modified Riser Value: " + str(riser)
        print
        tread_height_list.append(riser)
        # Calculate actual sight clearance
        act_clearance = (((y + riser + eye_level) * x) / (x + tread_size)) - (y + eye_level)
        deck_cvalues.append(act_clearance)
        #if act_clearance < sight_clearance and clear_flag == 0:
        #    clear_row = row + 1
        #    clear_flag = 1
        # Store coordinates in a list
        x = x + tread_size
        y = y + riser
        profile_point = rg.Point3d(x,y,0) #type: rg.Point3d
        profile_point.Transform(Xform)
        profile_list.append(profile_point)

        row += 1

    for i in xrange(len(profile_list)):
        tread_depth_list.append(tread_size)

    return profile_list, deck_cvalues, tread_height_list, tread_depth_list


# Draw_Pline
# This function draws the polylines for the deck tread profile and also
# for the stairs as well. It will return a list containing all of the profiles.
def Draw_Pline(o_plane, start_point, number_rows, start_distance, tread_elevation, tread_size, max_riser,
               riser_thickness, tread_thickness, profile_list_world):
    working_point_x = start_distance
    working_point_y = tread_elevation
    delta_x = start_point.X
    delta_y = start_point.Y
    module = 50.0
    x = []
    y = []
    local_deck_pts = []
    profile_list = []

    for i in profile_list_world:
        profile_list.append(rs.XformWorldToCPlane(i, o_plane))

    # First start at the bottom of the outer wall
    x.append(delta_x + working_point_x - (2 * riser_thickness + tread_size))
    y.append(delta_y + working_point_y - tread_thickness)
    x.append(delta_x + working_point_x - (2 * riser_thickness + tread_size))
    y.append(delta_y + working_point_y + 3 * tread_thickness)

    # Draw top of the wall
    x.append(delta_x + working_point_x - (riser_thickness + tread_size))
    y.append(delta_y + working_point_y + 3 * tread_thickness)

    # Inner Wall
    x.append(delta_x + working_point_x - (riser_thickness + tread_size))
    y.append(delta_y + working_point_y)

    # Extend first tread
    x.append(delta_x + working_point_x)
    y.append(delta_y + working_point_y)

    # Draw calculated risers and treads
    count = 1

    while count < number_rows:
        # Build the riser
        x.append(working_point_x + profile_list[count - 1].X - start_distance)
        y.append(working_point_y + profile_list[count].Y - tread_elevation)

        # Build the tread
        x.append(working_point_x + profile_list[count].X - start_distance)
        y.append(working_point_y + profile_list[count].Y - tread_elevation)

        count = count + 1

    # Build the bottom of the treads and risers.
    count = count - 1

    # First back of the last tread
    x.append(working_point_x + (profile_list[count].X - start_distance))
    y.append(working_point_y + (profile_list[count].Y - (tread_elevation + tread_thickness)))

    count = int(number_rows - 2)

    # Draw calculated riser backs and tread bottoms
    while count >= 0:
        # Tread Bottoms
        x.append(working_point_x + (profile_list[count].X - (start_distance - riser_thickness)))
        y.append(working_point_y + (profile_list[count + 1].Y - (tread_elevation + tread_thickness)))
        # Riser Backs
        x.append(working_point_x + (profile_list[count].X - (start_distance - riser_thickness)))
        y.append(working_point_y + (profile_list[count].Y - (tread_elevation + tread_thickness)))

        count = count - 1

    # Add the start point to close the profile
    x.append(delta_x + working_point_x - (2 * riser_thickness + tread_size))
    y.append(delta_y + working_point_y - tread_thickness)

    for i in xrange(len(x)):
        local_deck_pts.append(Rhino.Geometry.Point3d(rs.XformCPlaneToWorld((x[i], y[i], 0), o_plane)))

    # Draw Calculated Steps
    count = 1
    while count < number_rows:
        step_pts = []

        # Delete and values in the step point lists
        del x[:]
        del y[:]
        del step_pts[:]
        current_riser = profile_list[count].Y - profile_list[count - 1].Y

        # One Step
        if current_riser > max_riser / 3 and current_riser < max_riser * 2 / 3:
            # Tread Up
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + tread_size / 2)))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser / 2)))
            # Riser Across
            x.append(working_point_x + (profile_list[count - 1].X - start_distance))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser / 2)))
            # Tread Down
            x.append(working_point_x + (profile_list[count - 1].X - start_distance))
            y.append(working_point_y + (profile_list[count - 1].Y - tread_elevation))
            # Riser Back Across
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + tread_size / 2)))
            y.append(working_point_y + (profile_list[count - 1].Y - tread_elevation))
            # Tread Up Again to close
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + tread_size / 2)))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser / 2)))

        # Two Steps
        if current_riser >= max_riser * 2 / 3:
            # 1
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + (tread_size * 2 / 3))))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + (current_riser * 2 / 3))))

            # 2
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + (tread_size * 2 / 3))))
            y.append(working_point_y + (profile_list[count - 1].Y - tread_elevation))

            # 3
            x.append(working_point_x + (profile_list[count - 1].X - start_distance))
            y.append(working_point_y + (profile_list[count - 1].Y - tread_elevation))

            # 8
            x.append(working_point_x + (profile_list[count - 1].X - start_distance))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser / 3)))

            # 6
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + tread_size / 3)))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser / 3)))

            # 4
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + tread_size / 3)))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + current_riser * 2 / 3)))

            # 1
            x.append(working_point_x + (profile_list[count - 1].X - (start_distance + (tread_size * 2 / 3))))
            y.append(working_point_y + (profile_list[count].Y - (tread_elevation + (current_riser * 2 / 3))))

        for i in xrange(len(x)):
            step_pts.append(Rhino.Geometry.Point3d(rs.XformCPlaneToWorld((x[i], y[i], 0), o_plane)))

        Rhino.Geometry.PolylineCurve(step_pts)

        count = count + 1
    # print local_deck_pts
    pline = Rhino.Geometry.PolylineCurve(local_deck_pts)
    # print pline
    return pline


# Change the variable name of the input of the component to a
# standard name in the code. This way if we change the name on the component
# we dont have to change the code
sect_tree = section_params
p1_counter = 0
p2_counter = 0

deck_pts = DataTree[Rhino.Geometry.Point3d]()
row_c_value = DataTree[float]()
row_height = DataTree[float]()
row_depth = DataTree[float]()

deck_pline_temp = []
deck_pline_order = []
deck_polylines = DataTree[Rhino.Geometry.PolylineCurve]()


def Run_Polylines(i):
    deck2 = {'focal_point': first_origin,
             'last_point': last_pt[i],
             'number_rows': sect_tree.Branch(p1_counter, 0)[i],
             'start_distance': sect_tree.Branch(p1_counter, 1)[i],
             'tread_elevation': sect_tree.Branch(p1_counter, 2)[i],
             'tread_size': sect_tree.Branch(p1_counter, 3)[i],
             'max_riser': sect_tree.Branch(p1_counter, 4)[i],
             'riser_thickness': sect_tree.Branch(p1_counter, 8)[i],
             'tread_thickness': sect_tree.Branch(p1_counter, 9)[i]
             }
    deck_pline_temp.append(
        Draw_Pline(deck2['focal_point'], deck2['last_point'], deck2['number_rows'], deck2['start_distance'],
                   deck2['tread_elevation'], deck2['tread_size'], deck2['max_riser'],
                   deck2['riser_thickness'], deck2['tread_thickness'], deck_pts_temp[i]))
    deck_pline_order.append(i)

print type(sect_tree)
# Run this while loop for each section it has been given

while sect_tree.PathExists(GH_Path(p1_counter, p2_counter)):
    # Count the number of decks in the current section
    deck_count = len(sect_tree.Branch(GH_Path(p1_counter, p2_counter)))
    # Define the first origin plane for building our points
    first_origin = origin_planes.Branch(p1_counter)[0]
    # Create a varaible to store a list of points for each deck in the section
    deck_pts_temp = []
    cvalue_temp = []
    rheight_temp = []
    rdepth_temp = []
    last_pt = []
    last_pt.append(rs.XformWorldToCPlane(first_origin.Origin, first_origin))
    for i in xrange(deck_count):
        # Set the parameters for this deck
        deck = {'focal_point': first_origin,
                'last_point': last_pt[i],
                'number_rows': sect_tree.Branch(p1_counter, 0)[i],
                'start_distance': sect_tree.Branch(p1_counter, 1)[i],
                'tread_elevation': sect_tree.Branch(p1_counter, 2)[i],
                'tread_size': sect_tree.Branch(p1_counter, 3)[i],
                'max_riser': sect_tree.Branch(p1_counter, 4)[i],
                'min_increment': sect_tree.Branch(p1_counter, 5)[i],
                'eye_level': sect_tree.Branch(p1_counter, 6)[i],
                'sight_clearance': sect_tree.Branch(p1_counter, 7)[i],
                'riser_thickness': sect_tree.Branch(p1_counter, 8)[i],
                'tread_thickness': sect_tree.Branch(p1_counter, 9)[i]
                }
        pts, cvalue, rheight, rdepth = Calculate_Profile(deck['focal_point'], deck['last_point'], deck['number_rows'],
                                                         deck['start_distance'],
                                                         deck['tread_elevation'], deck['tread_size'], deck['max_riser'],
                                                         deck['min_increment'], deck['eye_level'],
                                                         deck['sight_clearance'],
                                                         deck['riser_thickness'], deck['tread_thickness'])
        deck_pts_temp.append(pts)
        cvalue_temp.append(cvalue)
        rheight_temp.append(rheight)
        rdepth_temp.append(rdepth)
        last_pt.append(rs.XformWorldToCPlane(deck_pts_temp[i][-1], first_origin))

    for i in xrange(len(deck_pts_temp)):
        path = GH_Path(p1_counter, i)
        deck_pts.AddRange(deck_pts_temp[i], path)
        row_c_value.AddRange(cvalue_temp[i], path)
        row_height.AddRange(rheight_temp[i], path)
        row_depth.AddRange(rdepth_temp[i], path)

    if parallel == True:
        tasks.Parallel.ForEach(xrange(deck_count), Run_Polylines)
    else:
        for i in xrange(deck_count):
            Run_Polylines(i)
    # Zip the deck_order and deck_temp files together so we can sort them
    zip_plines = zip(deck_pline_order, deck_pline_temp)
    zip_plines.sort()
    sorted_plines = []
    for i in xrange(len(zip_plines)):
        sorted_plines.append(zip_plines[i][1])
    path = GH_Path(p1_counter)
    # poly = scriptcontext.doc.Objects.Find(deck_pline_temp[i])
    deck_polylines.AddRange(sorted_plines, path)

    del deck_pts_temp[:]
    del cvalue_temp[:]
    del rheight_temp[:]
    del rdepth_temp[:]
    del deck_pline_temp[:]
    del deck_pline_order[:]
    del last_pt[:]

    # print p1_counter
    p1_counter = p1_counter + 1
    p2_counter = 0







