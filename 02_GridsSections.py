# Author: Paul F


import Rhino.Geometry as rg
from decimal import Decimal
import clr
clr.AddReference("Grasshopper")
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as DataTree
import math


# How many seating divisions will there be per segment type (width, length, corners?)
num_corner_div = 4
num_width_div = 5
num_length_div = 9

# Divide the curves coming from the field function and make grid lines
def Divide_Curves(safteyzone_offset_curves, num_corner_div, num_width_div, num_length_div):

    T_SweepPlanes = DataTree[rg.Plane]()

    sorted_curves = []
    curve_lengths = []

    # Go through all the curves coming from the boundary and
    # add them to nested, organized lists within "sorted_curves"
    for curve in safteyzone_offset_curves:
        length = round(Decimal(curve.GetLength()),2)
        if length not in curve_lengths:
            curve_lengths.append(length)
            sorted_curves.append([curve])
        else:
            index = curve_lengths.index(length)
            if index >= 0:
                sorted_curves[index].append(curve)

    # Sort the list...
    sorted(curve_lengths)
    # Then sort the list of curve lists by the sorted length list
    sorted_curves = [x for (y, x) in sorted(zip(curve_lengths, sorted_curves))]

    # Now all the curves can be added to named lists to keep track of them more easily
    sweep_corners = sorted_curves[0]
    sweep_widths = sorted_curves[1]
    sweep_lengths = sorted_curves[2]

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












