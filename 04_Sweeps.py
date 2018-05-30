# Author: Paul F
"""
Title: Sweeps
Description: Sweeps the section curves into bowl geometry by section
-
Provided by Idea Fellowship 2018.05.25
    Args:
    Returns

"""

import Rhino.Geometry as rg
from decimal import Decimal
import clr
clr.AddReference("Grasshopper")
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as DataTree
import math
import System.Drawing as sd


def Sweep_Section(T_SectionProfiles, T_ShatteredCurves):

    T_BowlSweeps = DataTree[rg.Brep]()
    #
    # for i in range (0, T_ShatteredCurves.BranchCount):
    #     myPath = T_ShatteredCurves.Paths[i]
    #     for j in range (0, len(T_ShatteredCurves.Branches[i])):
    #         sweepconstructor = rg.SweepOneRail()
    #         sweepprofile = T_SectionProfiles.Branches[i][j]
    #         sweeprail = T_ShatteredCurves.Branches[i][j]
    #         sweep = sweepconstructor.PerformSweep(sweeprail,sweepprofile)
    #
    #         T_BowlSweeps.AddRange(sweep,myPath)

    return T_BowlSweeps



test = Sweep_Section(T_SectionProfiles,T_SectionProfiles)