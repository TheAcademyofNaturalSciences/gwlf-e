# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

"""
Imported from CalcCNErosRunoffSed.bas
"""

import math
import logging
import numpy as np
from DailyArrayConverter import get_value_for_yesterday
from Water import Water_2
from LU import LU
from LU_1 import LU_1

from .enums import GrowFlag, LandUse

log = logging.getLogger(__name__)


def CalcCN(z, i, Y, j):
    """
    z - data model (public variables)
    i - month
    Y - year
    j - number of days in month
    """
    # Calculate Curve Number (CN)
    for l in range(z.NRur):

        if z.CN[l] > 0:
            if Water_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec)[Y][i][j] >= 0.2 * z.Retention[Y][i][j][l]:
                z.RurQRunoff[l][i] += z.Qrun[Y][i][j][l]

        z.ErosWashoff[l][i] = z.ErosWashoff[l][i] + z.RurEros[Y][i][j][l]

        if z.SedDelivRatio == 0:
            z.SedDelivRatio = 0.0001

    for l in range(z.NRur, z.NLU):
        z.WashImperv[l] = 0
        z.WashPerv[l] = 0

    for q in range(z.Nqual):
        z.NetSolidLoad[q] = 0
        z.NetDisLoad[q] = 0
    if Water_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec)[Y][i][j] < 0.05:
        pass
    else:
        for l in range(z.NRur, z.NLU):
            z.WashImperv[l] = (1 - math.exp(-1.81 * z.QrunI[Y][i][j][l])) * z.ImpervAccum[l]
            z.ImpervAccum[l] -= z.WashImperv[l]

            z.WashPerv[l] = (1 - math.exp(-1.81 * z.QrunP[Y][i][j][l])) * z.PervAccum[l]
            z.PervAccum[l] -= z.WashPerv[l]
            lu = LU(z.NRur, z.NUrb)
            z.UrbQRunoff[l][i] += (z.QrunI[Y][i][j][l] * (z.Imper[l] * (1 - z.ISRR[lu[l]]) * (1 - z.ISRA[lu[l]]))
                                   + z.QrunP[Y][i][j][l] * (
                                           1 - (z.Imper[l] * (1 - z.ISRR[lu[l]]) * (1 - z.ISRA[lu[l]]))))

    BasinWater(z, i, Y, j)


def BasinWater(z, i, Y, j):
    # BELOW ARE CALCULATIONS FOR URBAN LOADS
    # MAYBE THEY SHOULD BE IN "CALCULATE LOADS" SUBROUTINE???
    z.DissolvedLoad = 0
    z.SolidLoad = 0
    z.UrbLoadRed = 0

    if z.AdjUrbanQTotal_1[Y][i][j] > 0.001:
        for l in range(z.NRur, z.NLU):
            for q in range(z.Nqual):
                z.SolidBasinMass[q] = 0
                z.DisBasinMass[q] = 0

                if z.Storm > 0:
                    z.UrbLoadRed = (z.Water[Y][i][j] / z.Storm) * z.UrbBMPRed[l][q]
                else:
                    z.UrbLoadRed = 0

                if Water_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec)[Y][i][j] > z.Storm:
                    z.UrbLoadRed = z.UrbBMPRed[l][q]

                # TODO: Should 11 be NRur + 1?
                # What is this trying to do?
                lu_1 = LU_1(z.NRur, z.NUrb)

                if z.Area[l] > 0:
                    z.SurfaceLoad = (((z.LoadRateImp[l][q] * z.WashImperv[l] * (
                            (z.Imper[l] * (1 - z.ISRR[lu_1[l]]) * (1 - z.ISRA[lu_1[l]]))
                            * (z.SweepFrac[i] + (
                            (1 - z.SweepFrac[i]) * ((1 - z.UrbSweepFrac) * z.Area[l]) / z.Area[l])))
                                       + z.LoadRatePerv[l][q] * z.WashPerv[l] * (
                                               1 - (z.Imper[l] * (1 - z.ISRR[lu_1[l]]) * (1 - z.ISRA[lu_1[l]]))))
                                      * z.Area[l]) - z.UrbLoadRed)
                else:
                    z.SurfaceLoad = 0

                if z.SurfaceLoad < 0:
                    z.SurfaceLoad = 0

                z.DisSurfLoad = z.DisFract[l][q] * z.SurfaceLoad

                # Apply Bioretention and/or Stream Buffer BMP
                z.SurfaceLoad *= (1 - z.RetentionEff) * (1 - (z.FilterEff * z.PctStrmBuf))
                z.DisSurfLoad *= (1 - z.RetentionEff) * (1 - (z.FilterEff * z.PctStrmBuf))

                # Apply sediment detention basin BMP
                if z.BasinArea > 0 and z.Area[l] > 0:
                    z.SolidBasinMass[q] += z.SurfaceLoad - z.DisSurfLoad
                    z.DisBasinMass[q] += z.DisSurfLoad

                    z.DissolvedLoad = z.OutflowFract * z.DisBasinMass[q]
                    z.SolidLoad = z.Mixing * z.OutflowFract * z.SolidBasinMass[q]

                    z.SolidBasinMass[q] -= z.SolidLoad
                    z.DisBasinMass[q] -= z.DissolvedLoad

                    z.SurfaceLoad -= z.DissolvedLoad + z.SolidLoad
                    z.DisSurfLoad -= z.DissolvedLoad

                    z.LuLoad[Y][l][q] += z.DissolvedLoad + z.SolidLoad
                    z.LuDisLoad[Y][l][q] += z.DissolvedLoad

                    z.NetDisLoad[q] += z.DissolvedLoad
                    z.NetSolidLoad[q] += z.SolidLoad
                else:
                    z.LuLoad[Y][l][q] += z.SurfaceLoad
                    z.LuDisLoad[Y][l][q] += z.DisSurfLoad

                    z.NetDisLoad[q] += z.DisSurfLoad
                    z.NetSolidLoad[q] += z.SurfaceLoad - z.DisSurfLoad

    for q in range(z.Nqual):
        z.Load[Y][i][q] += z.NetDisLoad[q] + z.NetSolidLoad[q]
        z.DisLoad[Y][i][q] += z.NetDisLoad[q]

        if z.Load[Y][i][q] < 0:
            z.Load[Y][i][q] = 0

        if z.DisLoad[Y][i][q] < 0:
            z.DisLoad[Y][i][q] = 0

    # WATERSHED TOTALS

    z.RuralRunoff[Y][i] += z.RuralQTotal[Y][i][j]
    z.UrbanRunoff[Y][i] += z.UrbanQTotal_1[Y][i][j]
    # TODO: (Are z.AgRunoff and z.AgQTotal actually in cm?)
    # z.AgRunoff[Y][i] += z.AgQTotal[Y][i][j]

    # Convert Urban runoff from cm to Liters
    # TODO: (Maybe use z.UrbanRunoff[y][i] instead in the above equation)
    z.UrbRunoffLiter[Y][i] = (z.UrbanRunoff[Y][i] / 100) * z.UrbAreaTotal * 10000 * 1000

    # Calculate Daily runoff (used in output for daily flow file)
    if z.AdjQTotal[Y][i][j] > 0:
        z.DayRunoff[Y][i][j] = z.AdjQTotal[Y][i][j]
    elif z.QTotal[Y][i][j] > 0:
        z.DayRunoff[Y][i][j] = z.QTotal[Y][i][j]
    else:
        z.DayRunoff[Y][i][j] = 0
