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

# Divide the curves coming from the field function and make grid lines
def Divide_Curves(safteyzone_offset_curves, num_corner_div, num_width_div, num_length_div):

    T_SweepPlanes = DataTree[rg.Plane]()

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
        for val in tvals:
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Rotate(.5 * math.pi,z_vect)
            plane = rg.Plane(point,x_vect,z_vect)
            T_SweepPlanes.Add(plane,path1)

    # Add points on the curves to specify widths "grid" divisions
    for curve in sweep_widths:
        curve = curve.ToNurbsCurve()
        path2 = ghpath(2)
        curve.Domain = rg.Interval(0,1)
        tvals = curve.DivideByCount(num_width_div,True)
        for val in tvals:
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Rotate(.5 * math.pi,z_vect)
            plane = rg.Plane(point,x_vect,z_vect)
            T_SweepPlanes.Add(plane,path2)

    # Add points on the curves to specify corners "grid" divisions
    for curve in sweep_corners:
        curve = curve.ToNurbsCurve()
        path3 = ghpath(3)
        curve.Domain = rg.Interval(0, 1)
        tvals = curve.DivideByCount(num_corner_div, True)
        for val in tvals:
            point = curve.PointAt(val)
            z_vect = rg.Vector3d.ZAxis
            x_vect = curve.TangentAt(val)
            x_vect.Rotate(.5 * math.pi, z_vect)
            plane = rg.Plane(point, x_vect, z_vect)
            T_SweepPlanes.Add(plane, path3)

    return T_SweepPlanes



T_SweepPlanes = Divide_Curves(safetyzone_offset_curves, num_corner_div, num_width_div, num_length_div)












