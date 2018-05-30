# Author: Paul F
"""
Title: Grids for Sections
Description: creates planes which can be used to host the bowl section profile curves
-
Provided by Idea Fellowship 2018.05.25
    Args:
        safteyzone_offset_curves, num_corner_div, num_width_div, num_length_div
        :: List of curves representing the first row of seating along with the numbers of sections should be
        :: in each side of the bowl
    Returns
        T_SweepPlanes
        :: A tree of planes to host the section profiles
"""

import Rhino.Geometry as rg
from decimal import Decimal
import clr
clr.AddReference("Grasshopper")
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as DataTree
import math
import System.Drawing as sd


# How many seating divisions will there be per segment type (width, length, corners?)
num_corner_div = 4
num_width_div = 5
num_length_div = 9

# Divide the curves coming from the field function into sections
def Divide_Curves(safteyzone_offset_curves, num_corner_div, num_width_div, num_length_div):

    T_SweepPlanes = DataTree[rg.Plane]()
    T_ShatteredCurves = DataTree[rg.Curve]()
    T_ShatteredLines = DataTree[rg.Line]()

    sweep_corners = []
    sweep_widths = []
    sweep_lengths = []

    for i in range (0,len(safteyzone_offset_curves)):
        curve = safteyzone_offset_curves[i]
        if i == 0:
            sweep_widths.append(curve)
        elif i == 1:
            sweep_corners.append(curve)
        elif i == 2:
            sweep_lengths.append(curve)
        elif i == 3:
            sweep_corners.append(curve)
        elif i == 4:
            sweep_widths.append(curve)
        elif i == 5:
            sweep_corners.append(curve)
        elif i == 6:
            sweep_lengths.append(curve)
        elif i == 7:
            sweep_corners.append(curve)

    # Add points on the curves to specify lengths "grid" divisions
    for curve in sweep_lengths:
        curve = curve.ToNurbsCurve()
        path1 = ghpath(1)
        curve.Domain = rg.Interval(0,1)
        tvals = curve.DivideByCount(num_length_div,True)
        trimmed_tvals = []
        for i in range(0, len(tvals) - 1):
            val = tvals[i]
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Reverse()
            x_vect.Rotate(.5 * math.pi, z_vect)
            plane = rg.Plane(point, x_vect, z_vect)
            T_SweepPlanes.Add(plane, path1)
            trimmed_tvals.append(val)
        shatter = curve.Split(trimmed_tvals)
        for segment in shatter:
            segment.Domain = rg.Interval(0, 1)
            line = rg.Line(segment.PointAt(0),segment.PointAt(1))
            T_ShatteredLines.Add(line,path1)
            T_ShatteredCurves.Add(segment, path1)

    # Add points on the curves to specify widths "grid" divisions
    for curve in sweep_widths:
        curve = curve.ToNurbsCurve()
        path2 = ghpath(2)
        curve.Domain = rg.Interval(0,1)
        tvals = curve.DivideByCount(num_width_div,True)
        trimmed_tvals = []
        for i in range (0,len(tvals)-1):
            val = tvals[i]
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Reverse()
            x_vect.Rotate(.5 * math.pi,z_vect)
            plane = rg.Plane(point,x_vect,z_vect)
            T_SweepPlanes.Add(plane,path2)
            trimmed_tvals.append(val)
        shatter = curve.Split(trimmed_tvals)
        for segment in shatter:
            segment.Domain = rg.Interval(0, 1)
            line = rg.Line(segment.PointAt(0), segment.PointAt(1))
            T_ShatteredLines.Add(line, path2)
            T_ShatteredCurves.Add(segment, path2)

    # Add points on the curves to specify corners "grid" divisions
    for curve in sweep_corners:
        curve = curve.ToNurbsCurve()
        path3 = ghpath(3)
        curve.Domain = rg.Interval(0, 1)
        tvals = curve.DivideByCount(num_corner_div, True)
        trimmed_tvals = []
        for i in range(0, len(tvals) - 1):
            val = tvals[i]
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Reverse()
            x_vect.Rotate(.5 * math.pi, z_vect)
            plane = rg.Plane(point, x_vect, z_vect)
            T_SweepPlanes.Add(plane, path3)
            trimmed_tvals.append(val)
        shatter = curve.Split(trimmed_tvals)
        for segment in shatter:
            segment.Domain = rg.Interval(0, 1)
            line = rg.Line(segment.PointAt(0), segment.PointAt(1))
            T_ShatteredLines.Add(line, path3)
            T_ShatteredCurves.Add(segment, path3)


    return T_SweepPlanes,T_ShatteredCurves,T_ShatteredLines

# Helper Function to isolate segments by each main curve
def SplitList(InputList,PartitionCount):
    ItemCount = int(len(InputList)/PartitionCount)
    masterlist = []
    for i in range(0,PartitionCount):
        sublist = []
        for j in range(0,ItemCount):
            sublist.append(InputList[i*ItemCount + j])
        masterlist.append(sublist)

    return masterlist



# Remap the divided curves and points back to the correct field order. IE starting with lower
# bottom curve and working around clockwise
def Remap_Points_Curves(T_SweepPlanes,T_ShatteredLines):
    OrderedSegments = []
    OrderedPlanes = []

    ShortCurves = SplitList(T_ShatteredLines.Branches[1],2)
    print len(ShortCurves)


    Planes_01 = T_SweepPlanes.Branches[0]





# Find an averaged plane between each section for the sweep
def Average_Planes():
    pass



results = Divide_Curves(safetyzone_offset_curves, num_corner_div, num_width_div, num_length_div)
T_SweepPlanes = results[0]
T_ShatteredCurves = results[1]
T_ShatteredLines = results[2]

test = Remap_Points_Curves(T_SweepPlanes,T_ShatteredLines)











