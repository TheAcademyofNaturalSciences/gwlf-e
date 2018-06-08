# coding: utf-8
import logging
import numpy as np
from Memoization import memoize
from Timer import time_function
import json
import uuid
import csv
import re


# @time_function
@memoize
def AdjQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adj_urban_q_total = AdjUrbanQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                       Grow_0, CNP_0, Imper,
                                       ISRR, ISRA, Qretention, PctAreaInfil)
    rural_q_total = RuralQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    # Assume 20% reduction of runoff with urban wetlands
                    result[Y][i][j] = (adj_urban_q_total[Y][i][j] * (1 - (n25b * 0.2))) + rural_q_total[Y][i][j]
    return result

# @time_function
@memoize
def AdjQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12, 31))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adj_urban_q_total = AdjUrbanQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                       Grow_0, CNP_0, Imper,ISRR, ISRA, Qretention, PctAreaInfil)
    rural_q_total = RuralQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area)
    result[np.where((Temp>0) & (water>0.01))] = (adj_urban_q_total[np.where((Temp>0) & (water>0.01))]* (1 - (n25b * 0.2))) + rural_q_total[np.where((Temp>0) & (water>0.01))]
    return result


try:
    from gwlfe_compiled import AdjUrbanQTotal_2_inner
except ImportError:
    print("Unable to import compiled AdjUrbanQTotal_2_inner, using slower version")
    from AdjUrbanQTotal_2_inner import AdjUrbanQTotal_2_inner


# @time_function
@memoize
# @time_function
def AdjUrbanQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA, Qretention, PctAreaInfil):
    result = np.zeros((NYrs, 12, 31))
    adj_urban_q_total = 0  # used because this is a buffered variable
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urban_q_total = UrbanQTotal(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper, ISRR, ISRA)
    urb_area_total = UrbAreaTotal(NRur, NUrb, Area)
    area_total = AreaTotal(NRur, NUrb, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        # z.adj_urban_q_total = get_value_for_yesterday(z.adj_urban_q_total_1,0,Y,i,j,z.NYrs,z.DaysMonth)
                        pass
                    else:
                        adj_urban_q_total = urban_q_total[Y][i][j]
                        if Qretention > 0:
                            if urban_q_total[Y][i][j] > 0:
                                if urban_q_total[Y][i][j] <= Qretention * PctAreaInfil:
                                    adj_urban_q_total = 0
                                else:
                                    adj_urban_q_total = urban_q_total[Y][i][j] - Qretention * PctAreaInfil
                    if urb_area_total > 0:
                        adj_urban_q_total = adj_urban_q_total * urb_area_total / area_total
                    else:
                        adj_urban_q_total = 0
                else:
                    pass
                result[Y][i][j] = adj_urban_q_total
    return result


@memoize
def AdjUrbanQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, Qretention, PctAreaInfil):
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urban_q_total = UrbanQTotal_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA)
    urb_area_total = UrbAreaTotal_2(NRur, NUrb, Area)
    area_total = AreaTotal_2(Area)
    return AdjUrbanQTotal_2_inner(NYrs, DaysMonth, Temp, Qretention, PctAreaInfil, water, urban_q_total, urb_area_total,
                                  area_total)

# @jit
# def AdjUrbanQTotal_2_inner(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
#                    ISRR, ISRA, Qretention, PctAreaInfil,water,urban_q_total,urb_area_total,area_total):
#     result = np.zeros((NYrs, 12, 31))
#     adj_urban_q_total = 0
#     urban_q_total = DAC.ymd_to_daily(urban_q_total, DaysMonth)
#     Temp = DAC.ymd_to_daily(Temp, DaysMonth)
#     water = DAC.ymd_to_daily(water, DaysMonth)
#     for j in range(len(urban_q_total)):
#         if Temp[j] > 0 and water[j] > 0.01:
#             if water[j] <0.05:
#                 pass
#             else:
#                 adj_urban_q_total = urban_q_total[j]
#                 if Qretention > 0 and urban_q_total[j] > 0:
#                     if urban_q_total[j] <= Qretention * PctAreaInfil:
#                         adj_urban_q_total = 0
#                     else:
#                         adj_urban_q_total = urban_q_total[j] - Qretention * PctAreaInfil
#             if urb_area_total > 0:
#                 adj_urban_q_total = adj_urban_q_total * urb_area_total / area_total
#             else:
#                 adj_urban_q_total = 0
#         else:
#             pass
#         result[j] = adj_urban_q_total
#     return DAC.daily_to_ymd(result,NYrs, DaysMonth)



@memoize
def AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                     Imper, ISRR, ISRA, Qretention, PctAreaInfil):
    result = np.zeros((NYrs, 12, 31))
    adj_urban_q_total = AdjUrbanQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                       Grow_0, CNP_0, Imper,
                                       ISRR, ISRA, Qretention, PctAreaInfil)
    urb_area_total = UrbAreaTotal(NRur, NUrb, Area)
    area_total = AreaTotal(NRur, NUrb, Area)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i][j] = adj_urban_q_total[Y][i][j] * area_total / urb_area_total
                    # TODO: when I broke this cycle, the only way I could think to do this was to undo the calculation done at the end of adj_urban_q_total. Hopefully there is a better way
    return result

@memoize
def AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                     Imper, ISRR, ISRA, Qretention, PctAreaInfil):
    result = np.zeros((NYrs, 12, 31))
    adj_urban_q_total = AdjUrbanQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA, Qretention, PctAreaInfil)
    urb_area_total = UrbAreaTotal_2(NRur,NUrb,Area)
    area_total = AreaTotal_2(Area)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result[np.where((Temp >0) & (water > 0.01))] = adj_urban_q_total[np.where((Temp >0) & (water > 0.01))] * area_total / urb_area_total
    return result


def AEU(NumAnimals, AvgAnimalWt, NRur, NUrb, Area):
    # Recalculate AEU using the TotAEU from the animal file and the total area of the basin in Acres
    result = 0
    areatotal = AreaTotal(NRur, NUrb, Area)
    totLAEU = TotLAEU(NumAnimals, AvgAnimalWt)
    if totLAEU > 0 and areatotal > 0:
        result += totLAEU / (areatotal * 2.471)
    else:
        result = 0
    return result


def AEU_2(NumAnimals, AvgAnimalWt, Area):
    areatotal = AreaTotal_2(Area)
    totLAEU = TotLAEU(NumAnimals, AvgAnimalWt)
    if totLAEU > 0 and areatotal > 0:
        return totLAEU / (areatotal * 2.471)
    else:
        return 0

# -*- coding: utf-8 -*-

"""
Imported from AFOS.bas
"""


log = logging.getLogger(__name__)


def AnimalOperations(z, Y):
    for i in range(12):
        # z.LossFactAdj[Y][i] = (z.Precipitation[Y][i] / z.DaysMonth[Y][i]) / 0.3301

        # Non-grazing animal losses
        # z.NGLostManN[Y][i] = (z.NGAppManN[i] * z.NGAppNRate[i] * z.LossFactAdj[Y][i]
        #                       * (1 - z.NGPctSoilIncRate[i]))
        #
        # if z.NGLostManN[Y][i] > z.NGAppManN[i]:
        #     z.NGLostManN[Y][i] = z.NGAppManN[i]
        # if z.NGLostManN[Y][i] < 0:
        #     z.NGLostManN[Y][i] = 0

        z.NGLostManP[Y][i] = (z.NGAppManP[i] * z.NGAppPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                              * (1 - z.NGPctSoilIncRate[i]))

        if z.NGLostManP[Y][i] > z.NGAppManP[i]:
            z.NGLostManP[Y][i] = z.NGAppManP[i]
        if z.NGLostManP[Y][i] < 0:
            z.NGLostManP[Y][i] = 0

        z.NGLostManFC[Y][i] = (z.NGAppManFC[i] * z.NGAppFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                               * (1 - z.NGPctSoilIncRate[i]))

        if z.NGLostManFC[Y][i] > z.NGAppManFC[i]:
            z.NGLostManFC[Y][i] = z.NGAppManFC[i]
        if z.NGLostManFC[Y][i] < 0:
            z.NGLostManFC[Y][i] = 0

        # z.NGLostBarnN[Y][i] = (z.NGInitBarnN[i] * z.NGBarnNRate[i] * z.LossFactAdj[Y][i]
        #                        - z.NGInitBarnN[i] * z.NGBarnNRate[i] * z.LossFactAdj[Y][
        #                            i] * z.AWMSNgPct * z.NgAWMSCoeffN
        #                        + z.NGInitBarnN[i] * z.NGBarnNRate[i] * z.LossFactAdj[Y][
        #                            i] * z.RunContPct * z.RunConCoeffN)
        #
        # if z.NGLostBarnN[Y][i] > z.NGInitBarnN[i]:
        #     z.NGLostBarnN[Y][i] = z.NGInitBarnN[i]
        # if z.NGLostBarnN[Y][i] < 0:
        #     z.NGLostBarnN[Y][i] = 0

        z.NGLostBarnP[Y][i] = (z.NGInitBarnP[i] * z.NGBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                               - z.NGInitBarnP[i] * z.NGBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                   i] * z.AWMSNgPct * z.NgAWMSCoeffP
                               + z.NGInitBarnP[i] * z.NGBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                   i] * z.RunContPct * z.RunConCoeffP)

        if z.NGLostBarnP[Y][i] > z.NGInitBarnP[i]:
            z.NGLostBarnP[Y][i] = z.NGInitBarnP[i]
        if z.NGLostBarnP[Y][i] < 0:
            z.NGLostBarnP[Y][i] = 0

        z.NGLostBarnFC[Y][i] = (z.NGInitBarnFC[i] * z.NGBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                                - z.NGInitBarnFC[i] * z.NGBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                    i] * z.AWMSNgPct * z.NgAWMSCoeffP
                                + z.NGInitBarnFC[i] * z.NGBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                    i] * z.RunContPct * z.RunConCoeffP)

        if z.NGLostBarnFC[Y][i] > z.NGInitBarnFC[i]:
            z.NGLostBarnFC[Y][i] = z.NGInitBarnFC[i]
        if z.NGLostBarnFC[Y][i] < 0:
            z.NGLostBarnFC[Y][i] = 0

        # Grazing animal losses
        # z.GRLostManN[Y][i] = (z.GRAppManN[i] * z.GRAppNRate[i] * z.LossFactAdj[Y][i]
        #                       * (1 - z.GRPctSoilIncRate[i]))
        #
        # if z.GRLostManN[Y][i] > z.GRAppManN[i]:
        #     z.GRLostManN[Y][i] = z.GRAppManN[i]
        # if z.GRLostManN[Y][i] < 0:
        #     z.GRLostManN[Y][i] = 0

        z.GRLostManP[Y][i] = (z.GRAppManP[i] * z.GRAppPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                              * (1 - z.GRPctSoilIncRate[i]))

        if z.GRLostManP[Y][i] > z.GRAppManP[i]:
            z.GRLostManP[Y][i] = z.GRAppManP[i]
        if z.GRLostManP[Y][i] < 0:
            z.GRLostManP[Y][i] = 0

        z.GRLostManFC[Y][i] = (z.GRAppManFC[i] * z.GRAppFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                               * (1 - z.GRPctSoilIncRate[i]))

        if z.GRLostManFC[Y][i] > z.GRAppManFC[i]:
            z.GRLostManFC[Y][i] = z.GRAppManFC[i]
        if z.GRLostManFC[Y][i] < 0:
            z.GRLostManFC[Y][i] = 0

        # z.GRLostBarnN[Y][i] = (z.GRInitBarnN[i] * z.GRBarnNRate[i] * z.LossFactAdj[Y][i]
        #                        - z.GRInitBarnN[i] * z.GRBarnNRate[i] * z.LossFactAdj[Y][
        #                            i] * z.AWMSGrPct * z.GrAWMSCoeffN
        #                        + z.GRInitBarnN[i] * z.GRBarnNRate[i] * z.LossFactAdj[Y][
        #                            i] * z.RunContPct * z.RunConCoeffN)
        #
        # if z.GRLostBarnN[Y][i] > z.GRInitBarnN[i]:
        #     z.GRLostBarnN[Y][i] = z.GRInitBarnN[i]
        # if z.GRLostBarnN[Y][i] < 0:
        #     z.GRLostBarnN[Y][i] = 0

        z.GRLostBarnP[Y][i] = (z.GRInitBarnP[i] * z.GRBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                               - z.GRInitBarnP[i] * z.GRBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                   i] * z.AWMSGrPct * z.GrAWMSCoeffP
                               + z.GRInitBarnP[i] * z.GRBarnPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                   i] * z.RunContPct * z.RunConCoeffP)

        if z.GRLostBarnP[Y][i] > z.GRInitBarnP[i]:
            z.GRLostBarnP[Y][i] = z.GRInitBarnP[i]
        if z.GRLostBarnP[Y][i] < 0:
            z.GRLostBarnP[Y][i] = 0

        z.GRLostBarnFC[Y][i] = (z.GRInitBarnFC[i] * z.GRBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i]
                                - z.GRInitBarnFC[i] * z.GRBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                    i] * z.AWMSGrPct * z.GrAWMSCoeffP
                                + z.GRInitBarnFC[i] * z.GRBarnFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][
                                    i] * z.RunContPct * z.RunConCoeffP)

        if z.GRLostBarnFC[Y][i] > z.GRInitBarnFC[i]:
            z.GRLostBarnFC[Y][i] = z.GRInitBarnFC[i]
        if z.GRLostBarnFC[Y][i] < 0:
            z.GRLostBarnFC[Y][i] = 0

        # z.GRLossN[Y][i] = ((z.GrazingN[i] - z.GRStreamN[i])
        #                    * z.GrazingNRate[i] * z.LossFactAdj[Y][i])
        #
        # if z.GRLossN[Y][i] > (z.GrazingN[i] - z.GRStreamN[i]):
        #     z.GRLossN[Y][i] = (z.GrazingN[i] - z.GRStreamN[i])
        # if z.GRLossN[Y][i] < 0:
        #     z.GRLossN[Y][i] = 0

        z.GRLossP[Y][i] = ((z.GrazingP[i] - z.GRStreamP[i])
                           * z.GrazingPRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i])

        if z.GRLossP[Y][i] > (z.GrazingP[i] - z.GRStreamP[i]):
            z.GRLossP[Y][i] = (z.GrazingP[i] - z.GRStreamP[i])
        if z.GRLossP[Y][i] < 0:
            z.GRLossP[Y][i] = 0

        z.GRLossFC[Y][i] = ((z.GrazingFC[i] - z.GRStreamFC[i])
                            * z.GrazingFCRate[i] * LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i])

        if z.GRLossFC[Y][i] > (z.GrazingFC[i] - z.GRStreamFC[i]):
            z.GRLossFC[Y][i] = (z.GrazingFC[i] - z.GRStreamFC[i])
        if z.GRLossFC[Y][i] < 0:
            z.GRLossFC[Y][i] = 0

        # Total animal related losses
        # z.AnimalN[Y][i] = (z.NGLostManN[Y][i]
        #                    + z.GRLostManN[Y][i]
        #                    + z.NGLostBarnN[Y][i]
        #                    + z.GRLostBarnN[Y][i]
        #                    + z.GRLossN[Y][i]
        #                    + z.GRStreamN[i])

        z.AnimalP[Y][i] = ((z.NGLostManP[Y][i]
                           + z.GRLostManP[Y][i]
                           + z.NGLostBarnP[Y][i]
                           + z.GRLostBarnP[Y][i]
                           + z.GRLossP[Y][i]
                           + z.GRStreamP[i])
                           - ((z.NGLostManP[Y][i] + z.NGLostBarnP[Y][i]) * z.PhytasePct * z.PhytaseCoeff))

        z.AnimalFC[Y][i] = (z.NGLostManFC[Y][i]
                            + z.GRLostManFC[Y][i]
                            + z.NGLostBarnFC[Y][i]
                            + z.GRLostBarnFC[Y][i]
                            + z.GRLossFC[Y][i]
                            + z.GRStreamFC[i])

        # CACULATE PATHOGEN LOADS
        z.ForestAreaTotalSqMi = 0
        z.ForestAreaTotalSqMi = (z.ForestAreaTotal * 0.01) / 2.59

        z.PtFlowLiters = (z.PointFlow[i] / 100) * TotAreaMeters(z.NRur, z.NUrb, z.Area) * 1000

        # Get the wildlife orgs
        z.WWOrgs[Y][i] = z.PtFlowLiters * (z.WWTPConc * 10) * (1 - z.InstreamDieoff)
        z.SSOrgs[Y][i] = (z.SepticOrgsDay
                          * z.SepticsDay[i]
                          * z.DaysMonth[Y][i]
                          * z.SepticFailure
                          * (1 - z.InstreamDieoff))

        if LossFactAdj_2(z.Prec, z.DaysMonth)[Y][i] * (1 - z.WuDieoff) > 1:
            z.UrbOrgs[Y][i] = (z.UrbRunoffLiter[Y][i]
                               * (z.UrbEMC * 10)
                               * (1 - z.InstreamDieoff))
            z.WildOrgs[Y][i] = (z.WildOrgsDay
                                * z.DaysMonth[Y][i]
                                * z.WildDensity
                                * z.ForestAreaTotalSqMi
                                * (1 - z.InstreamDieoff))
        else:
            z.UrbOrgs[Y][i] = (
                    UrbRunoffLiter_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.NUrb, z.Area,
                                     z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA)[Y][i]
                               * (z.UrbEMC * 10)
                               * (1 - z.WuDieoff)
                               * (1 - z.InstreamDieoff))
            z.WildOrgs[Y][i] = (z.WildOrgsDay
                                * z.DaysMonth[Y][i]
                                * z.WildDensity
                                * z.ForestAreaTotalSqMi
                                * (1 - z.WuDieoff)
                                * (1 - z.InstreamDieoff))

        # Get the total orgs
        z.TotalOrgs[Y][i] = (z.WWOrgs[Y][i]
                             + z.SSOrgs[Y][i]
                             + z.UrbOrgs[Y][i]
                             + z.WildOrgs[Y][i]
                             + z.AnimalFC[Y][i])

        z.CMStream[Y][i] = (StreamFlow_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                         z.CNI_0,
                                         z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                         z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                         z.SatStor_0,
                                         z.RecessionCoef, z.SeepCoef
                                         , z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity,
                                         z.PointFlow,
                                         z.StreamWithdrawal,
                                         z.GroundWithdrawal)[Y][i] / 100) * TotAreaMeters(z.NRur, z.NUrb, z.Area)

        if z.CMStream[Y][i] > 0:
            z.OrgConc[Y][i] = (z.TotalOrgs[Y][i] / (z.CMStream[Y][i] * 1000)) / 10
        else:
            z.OrgConc[Y][i] = 0



# @memoize
def AgAreaTotal(NRur, Landuse_2, Area):
    result = 0
    for l in range(NRur):
        if Landuse_2[l] is LandUse.FOREST:
            pass
        elif Landuse_2[l] is LandUse.CROPLAND:
            result += Area[l]
        elif Landuse_2[l] is LandUse.HAY_PAST:
            result += Area[l]
        elif Landuse_2[l] is LandUse.TURFGRASS:
            result += Area[l]
    return result

# vectorization is slower
# @time_function
# def AgAreaTotal_2(Landuse, Area):
#     return Area[Landuse == LandUseNames.CROPLAND] + \
#            Area[Landuse == LandUseNames.HAY_PAST] + \
#            Area[Landuse == LandUseNames.TURFGRASS]



@memoize
def AgQTotal(NYrs,DaysMonth,InitSnow_0, Temp, Prec,NRur,CN, AntMoist_0,NUrb,Grow_0,Landuse,Area):
    result = np.zeros((NYrs,12,31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    retention = Retention(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)
    q_run = Qrun(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)
    ag_area_total = AgAreaTotal(NRur, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = 0

                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        if CN[l] > 0:
                            if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                                if Landuse[l] is LandUse.CROPLAND:
                                    # (Maybe used for STREAMPLAN?)
                                    result[Y][i][j] += q_run[Y][i][j][l] * Area[l]
                                    # z.AgQRunoff[l][i] += z.Qrun[Y][i][j][l]
                                elif Landuse[l] is LandUse.HAY_PAST:
                                    result[Y][i][j] += q_run[Y][i][j][l] * Area[l]
                                    # z.AgQRunoff[l][i] += z.Qrun[Y][i][j][l]
                                elif Landuse[l] is LandUse.TURFGRASS:
                                    result[Y][i][j] += q_run[Y][i][j][l] * Area[l]
                                    # z.AgQRunoff[l][i] += z.Qrun[Y][i][j][l]
                    if ag_area_total > 0:
                        result[Y][i][j] = result[Y][i][j] / ag_area_total
                    else:
                        result[Y][i][j] = 0
    return result

@memoize
def AgQTotal_2(NYrs,DaysMonth,InitSnow_0, Temp, Prec,NRur,CN, AntMoist_0,NUrb,Grow_0,Landuse,Area):
    result = np.zeros((NYrs, 12, 31))
    q_run = Qrun_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)
    ag_area_total = AgAreaTotal(NRur, Landuse, Area)
    ag_used = np.array([1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0])
    ag_area = Area * ag_used
    qrun_agarea = q_run * ag_area
    result = np.sum(qrun_agarea, axis=3) / ag_area_total
    return result


@memoize
def AgRunoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area):
    result = np.zeros((NYrs, 12))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    ag_q_total = AgQTotal(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i] += ag_q_total[Y][i][j]
    return result


@memoize
def AgRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area):
    result = np.zeros((NYrs, 12, 31))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    ag_q_total = AgQTotal_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area)
    result[np.where((Temp > 0) & (water > 0.01))] = ag_q_total[np.where((Temp > 0) & (water > 0.01))]
    return np.sum(result, axis=2)



@memoize
def AGSTRM(AgLength, StreamLength):
    result = 0.0
    result = AgLength / StreamLength if StreamLength > 0 else 0
    return result


def AGSTRM_2(AgLength, StreamLength):
    if(StreamLength > 0):
        return AgLength / StreamLength
    else:
        return 0


try:
    from gwlfe_compiled import AMC5_yesterday_inner
except ImportError:
    print("Unable to import compiled AMC5_yesterday_inner, using slower version")
    from AMC5_yesterday_inner import AMC5_yesterday_inner


# AMC5_yesterday returns the same value as yesterday(AMC5) and faster than any other version
@memoize
def AMC5(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0):
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    AMC5 = 0
    AntMoist = copy.deepcopy(AntMoist_0)
    for k in range(5):
        AMC5 += AntMoist[k]
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                AMC5 = AMC5 - AntMoist[4] + water[Y][i][j]
                AntMoist[4] = AntMoist[3]
                AntMoist[3] = AntMoist[2]
                AntMoist[2] = AntMoist[1]
                AntMoist[1] = AntMoist[0]
                AntMoist[0] = water[Y][i][j]

                result[Y][i][j] = AMC5  # TODO: why did this fix the mismatch of amc5?

    return result


# @time_function
# @jit(cache=True)
# def AMC5_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0):
#     result = np.zeros((NYrs, 12, 31))
#     water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
#     AMC5 = 0
#     AntMoist = copy.deepcopy(AntMoist_0)
#     AMC5 = np.sum(AntMoist)
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 AMC5 = AMC5 - AntMoist[4] + water[Y][i][j]
#                 AntMoist[4] = AntMoist[3]
#                 AntMoist[3] = AntMoist[2]
#                 AntMoist[2] = AntMoist[1]
#                 AntMoist[1] = AntMoist[0]
#                 AntMoist[0] = water[Y][i][j]
#
#                 result[Y][i][j] = AMC5  # TODO: why did this fix the mismatch of amc5?
#
#     return result


def AMC5_1(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0):
    result = np.zeros((NYrs, 12, 31))
    AntMoist1 = np.zeros((5,))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    AMC5 = 0
    for k in range(5):
        AMC5 += AntMoist_0[k]
        AntMoist1[k] = AntMoist_0[k]
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = AMC5
                AMC5 = AMC5 - AntMoist1[4] + water[Y][i][j]
                AntMoist1[4] = AntMoist1[3]
                AntMoist1[3] = AntMoist1[2]
                AntMoist1[2] = AntMoist1[1]
                AntMoist1[1] = AntMoist1[0]
                AntMoist1[0] = water[Y][i][j]
    return result


def AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0):
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    return AMC5_yesterday_inner(NYrs, DaysMonth, AntMoist_0, water)

# -*- coding: utf-8 -*-

"""
Imported from AnnualMeans.bas
"""


log = logging.getLogger(__name__)


def CalculateAnnualMeanLoads(z, Y):
    # UPDATE SEPTIC SYSTEM AVERAGES
    z.AvSeptNitr += z.SepticNitr[Y] / z.NYrs
    z.AvSeptPhos += z.SepticPhos[Y] / z.NYrs

    # Add the Stream Bank Erosion to sediment yield
    # for i in range(12):
    #     z.SedYield[Y][i] += z.StreamBankEros_2[Y][i] / 1000

    z.CalendarYr = z.WxYrBeg + (Y - 1)

    # CALCULATE ANNUAL MEANS FOR STREAM BANK AND TILE DRAINAGE VALUES
    # z.AvPtSrcFlow = AvPtSrcFlow(z.NYrs,z.PtSrcFlow)
    z.AvPtSrcFlow = AvPtSrcFlow_2(z.PointFlow)
    for i in range(12):
        z.AvStreamBankP[i] += z.StreamBankP[Y][i] / z.NYrs
        z.AvTileDrainN[i] += z.TileDrainN[Y][i] / z.NYrs
        z.AvTileDrainP[i] += z.TileDrainP[Y][i] / z.NYrs
        z.AvTileDrainSed[i] += z.TileDrainSed[Y][i] / z.NYrs

    # COMPUTE ANNUAL MEANS
    z.AvPrecipitation = AvPrecipitation_2(z.Prec)
    for i in range(12):
        z.AvDisNitr[i] += z.DisNitr[Y][i] / z.NYrs
        z.AvTotNitr[i] += z.TotNitr[Y][i] / z.NYrs
        z.AvDisPhos[i] += z.DisPhos[Y][i] / z.NYrs
        z.AvTotPhos[i] += z.TotPhos[Y][i] / z.NYrs
        z.AvGroundNitr[i] += z.GroundNitr[Y][i] / z.NYrs
        z.AvGroundPhos[i] += z.GroundPhos[Y][i] / z.NYrs
        # z.AvAnimalN[i] += z.AnimalN[Y][i] / z.NYrs
        z.AvAnimalP[i] += z.AnimalP[Y][i] / z.NYrs

        # z.AvGRLostBarnN[i] += z.GRLostBarnN[Y][i] / z.NYrs
        z.AvGRLostBarnP[i] += z.GRLostBarnP[Y][i] / z.NYrs
        z.AvGRLostBarnFC[i] += z.GRLostBarnFC[Y][i] / z.NYrs

        # z.AvNGLostBarnN[i] += z.NGLostBarnN[Y][i] / z.NYrs
        z.AvNGLostBarnP[i] += z.NGLostBarnP[Y][i] / z.NYrs
        z.AvNGLostBarnFC[i] += z.NGLostBarnFC[Y][i] / z.NYrs

        z.AvNGLostManP[i] += z.NGLostManP[Y][i] / z.NYrs

        # Average pathogen totals
        z.AvAnimalFC[i] += z.AnimalFC[Y][i] / z.NYrs
        z.AvWWOrgs[i] += z.WWOrgs[Y][i] / z.NYrs
        z.AvSSOrgs[i] += z.SSOrgs[Y][i] / z.NYrs
        z.AvUrbOrgs[i] += z.UrbOrgs[Y][i] / z.NYrs
        z.AvWildOrgs[i] += z.WildOrgs[Y][i] / z.NYrs
        z.AvTotalOrgs[i] += z.TotalOrgs[Y][i] / z.NYrs

    # Average loads for each landuse
    for l in range(z.NRur):
        z.AvLuRunoff[l] += \
            LuRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.NUrb, z.CNI_0, z.CNP_0,
                       z.AntMoist_0, z.Grow_0, z.Imper, z.ISRR, z.ISRA, z.CN)[Y][l] / z.NYrs
        z.AvLuErosion[l] += \
            LuRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.NUrb, z.CNI_0, z.CNP_0,
                       z.AntMoist_0, z.Grow_0, z.Imper, z.ISRR, z.ISRA, z.CN)[Y][l] / z.NYrs
        z.AvLuSedYield[l] += z.LuSedYield[Y][l] / z.NYrs
        z.AvLuDisNitr[l] += z.LuDisNitr[Y][l] / z.NYrs
        z.AvLuTotNitr[l] += z.LuTotNitr[Y][l] / z.NYrs
        z.AvLuDisPhos[l] += z.LuDisPhos[Y][l] / z.NYrs
        z.AvLuTotPhos[l] += z.LuTotPhos[Y][l] / z.NYrs

    for l in range(z.NRur, z.NLU):
        z.AvLuRunoff[l] += \
            LuRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.NUrb, z.CNI_0, z.CNP_0,
                       z.AntMoist_0, z.Grow_0, z.Imper, z.ISRR, z.ISRA, z.CN)[Y][l] / z.NYrs
        z.AvLuTotNitr[l] += z.LuTotNitr[Y][l] / z.NYrs
        z.AvLuTotPhos[l] += z.LuTotPhos[Y][l] / z.NYrs
        z.AvLuDisNitr[l] += z.LuDisNitr[Y][l] / z.NYrs
        z.AvLuDisPhos[l] += z.LuDisPhos[Y][l] / z.NYrs
        z.AvLuSedYield[l] += z.LuSedYield[Y][l] / z.NYrs

    z.AvStreamBankErosSum = sum(
        AvStreamBankEros_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                           z.PcntET,
                           z.DayHrs, z.MaxWaterCap, z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Qretention,
                           z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal,
                           z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
                           z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45,
                           z.n85, z.UrbBankStab))
    # z.AvStreamBankNSum = sum(z.AvStreamBankN)
    z.AvStreamBankPSum = sum(z.AvStreamBankP)
    z.AvPtSrcFlowSum = sum(z.AvPtSrcFlow)
    z.AvTileDrainSum = sum(AvTileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                         z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                         z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                         z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                         z.Landuse, z.TileDrainDensity))
    z.AvWithdrawalSum = sum(AvWithdrawal_2(z.NYrs, z.StreamWithdrawal, z.GroundWithdrawal))
    z.AvTileDrainNSum = sum(z.AvTileDrainN)
    z.AvTileDrainPSum = sum(z.AvTileDrainP)
    z.AvTileDrainSedSum = sum(z.AvTileDrainSed)
    # z.AvPrecipitationSum = sum(z.AvPrecipitation)
    z.AvEvapoTransSum = sum(
        AvEvapoTrans_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0, z.AntMoist_0,
                       z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs,
                       z.MaxWaterCap))
    z.AvGroundWaterSum = sum(
        AvGroundWater_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                        z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET,
                        z.DayHrs, z.MaxWaterCap,
                        z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Landuse, z.TileDrainDensity))
    z.AvRunoffSum = sum(AvRunoff_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                                   z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.Qretention,
                                   z.PctAreaInfil,
                                   z.n25b, z.CN, z.Landuse, z.TileDrainDensity))
    z.AvErosionSum = sum(
        AvErosion_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0, z.AntMoist_0,
                                  z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                  z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                                  z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0,
                                  z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab,
                                  z.SedDelivRatio_0, z.Acoef, z.KF, z.LS, z.C, z.P))
    z.AvSedYieldSum = sum(
        AvSedYield_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                     z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                     z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                     z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                     z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt,
                     z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength,
                     z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab, z.Acoef, z.KF,
                     z.LS, z.C, z.P, z.SedDelivRatio_0))
    z.AvDisNitrSum = sum(z.AvDisNitr)
    z.AvTotNitrSum = sum(z.AvTotNitr)
    z.AvDisPhosSum = sum(z.AvDisPhos)
    z.AvTotPhosSum = sum(z.AvTotPhos)
    z.AvGroundNitrSum = sum(z.AvGroundNitr)
    z.AvGroundPhosSum = sum(z.AvGroundPhos)
    # z.AvAnimalNSum = sum(z.AvAnimalN)
    z.AvAnimalPSum = sum(z.AvAnimalP)
    # z.AvGRLostBarnNSum = sum(z.AvGRLostBarnN)
    z.AvGRLostBarnPSum = sum(z.AvGRLostBarnP)
    z.AvGRLostBarnFCSum = sum(z.AvGRLostBarnFC)
    # z.AvNGLostBarnNSum = sum(z.AvNGLostBarnN)
    z.AvNGLostBarnPSum = sum(z.AvNGLostBarnP)
    z.AvNGLostBarnFCSum = sum(z.AvNGLostBarnFC)
    z.AvNGLostManPSum = sum(z.AvNGLostManP)
    z.AvAnimalFCSum = sum(z.AvAnimalFC)
    z.AvWWOrgsSum = sum(z.AvWWOrgs)
    z.AvSSOrgsSum = sum(z.AvSSOrgs)
    z.AvUrbOrgsSum = sum(z.AvUrbOrgs)
    z.AvWildOrgsSum = sum(z.AvWildOrgs)
    z.AvTotalOrgsSum = sum(z.AvTotalOrgs)
    z.AvLuRunoffSum = sum(z.AvLuRunoff)
    z.AvLuErosionSum = sum(z.AvLuErosion)
    z.AvLuSedYieldSum = sum(z.AvLuSedYield)
    z.AvLuDisNitrSum = sum(z.AvLuDisNitr)
    z.AvLuTotNitrSum = sum(z.AvLuTotNitr)
    z.AvLuDisPhosSum = sum(z.AvLuDisPhos)
    z.AvLuTotPhosSum = sum(z.AvLuTotPhos)



@time_function
def old_way(z):
    for Y in range(z.NYrs):
        for i in range(12):
            z.AvDisNitr[i] += z.DisNitr[Y][i] / z.NYrs
            z.AvTotNitr[i] += z.TotNitr[Y][i] / z.NYrs
            z.AvDisPhos[i] += z.DisPhos[Y][i] / z.NYrs
            z.AvTotPhos[i] += z.TotPhos[Y][i] / z.NYrs
            z.AvGroundNitr[i] += z.GroundNitr[Y][i] / z.NYrs
            z.AvGroundPhos[i] += z.GroundPhos[Y][i] / z.NYrs
            z.AvAnimalN[i] += z.AnimalN[Y][i] / z.NYrs
            z.AvAnimalP[i] += z.AnimalP[Y][i] / z.NYrs

            z.AvGRLostBarnN[i] += z.GRLostBarnN[Y][i] / z.NYrs
            z.AvGRLostBarnP[i] += z.GRLostBarnP[Y][i] / z.NYrs
            z.AvGRLostBarnFC[i] += z.GRLostBarnFC[Y][i] / z.NYrs

            z.AvNGLostBarnN[i] += z.NGLostBarnN[Y][i] / z.NYrs
            z.AvNGLostBarnP[i] += z.NGLostBarnP[Y][i] / z.NYrs
            z.AvNGLostBarnFC[i] += z.NGLostBarnFC[Y][i] / z.NYrs

            z.AvNGLostManP[i] += z.NGLostManP[Y][i] / z.NYrs

            # Average pathogen totals
            z.AvAnimalFC[i] += z.AnimalFC[Y][i] / z.NYrs
            z.AvWWOrgs[i] += z.WWOrgs[Y][i] / z.NYrs
            z.AvSSOrgs[i] += z.SSOrgs[Y][i] / z.NYrs
            z.AvUrbOrgs[i] += z.UrbOrgs[Y][i] / z.NYrs
            z.AvWildOrgs[i] += z.WildOrgs[Y][i] / z.NYrs
            z.AvTotalOrgs[i] += z.TotalOrgs[Y][i] / z.NYrs


@time_function
def numpy1(z):
    z.AvDisNitr = np.sum(z.DisNitr, axis=0) / z.NYrs
    z.AvTotNitr = np.sum(z.TotNitr, axis=0) / z.NYrs
    z.AvDisPhos = np.sum(z.DisPhos, axis=0) / z.NYrs
    z.AvTotPhos = np.sum(z.TotPhos, axis=0) / z.NYrs
    z.AvGroundNitr = np.sum(z.GroundNitr, axis=0) / z.NYrs
    z.AvGroundPhos = np.sum(z.GroundPhos, axis=0) / z.NYrs
    z.AvAnimalN = np.sum(z.AnimalN, axis=0) / z.NYrs
    z.AvAnimalP = np.sum(z.AnimalP, axis=0) / z.NYrs

    z.AvGRLostBarnN = np.sum(z.GRLostBarnN, axis=0) / z.NYrs
    z.AvGRLostBarnP = np.sum(z.GRLostBarnP, axis=0) / z.NYrs
    z.AvGRLostBarnFC = np.sum(z.GRLostBarnFC, axis=0) / z.NYrs

    z.AvNGLostBarnN = np.sum(z.NGLostBarnN, axis=0) / z.NYrs
    z.AvNGLostBarnP = np.sum(z.NGLostBarnP, axis=0) / z.NYrs
    z.AvNGLostBarnFC = np.sum(z.NGLostBarnFC, axis=0) / z.NYrs

    z.AvNGLostManP = np.sum(z.NGLostManP, axis=0) / z.NYrs

    # Average pathogen totals
    z.AvAnimalFC = np.sum(z.AnimalFC, axis=0) / z.NYrs
    z.AvWWOrgs = np.sum(z.WWOrgs, axis=0) / z.NYrs
    z.AvSSOrgs = np.sum(z.SSOrgs, axis=0) / z.NYrs
    z.AvUrbOrgs = np.sum(z.UrbOrgs, axis=0) / z.NYrs
    z.AvWildOrgs = np.sum(z.WildOrgs, axis=0) / z.NYrs
    z.AvTotalOrgs = np.sum(z.TotalOrgs, axis=0) / z.NYrs


@time_function
def numpy2(z):
    temp = np.vstack((z.DisNitr, z.TotNitr, z.DisPhos, z.TotPhos, z.GroundNitr, z.GroundPhos, z.AnimalN, z.AnimalP,
                      z.GRLostBarnN, z.GRLostBarnP, z.GRLostBarnFC, z.NGLostBarnN, z.NGLostBarnP, z.NGLostBarnFC,
                      z.NGLostManP, z.AnimalFC, z.WWOrgs, z.SSOrgs, z.UrbOrgs, z.WildOrgs, z.TotalOrgs))
    temp2 = np.sum(temp.reshape(-1, 15, 12), axis=1) / z.NYrs
    z.AvDisNitr = temp2[0]
    z.AvTotNitr = temp2[1]
    z.AvDisPhos = temp2[2]
    z.AvTotPhos = temp2[3]
    z.AvGroundNitr = temp2[4]
    z.AvGroundPhos = temp2[5]
    z.AvAnimalN = temp2[6]
    z.AvAnimalP = temp2[7]

    z.AvGRLostBarnN = temp2[8]
    z.AvGRLostBarnP = temp2[9]
    z.AvGRLostBarnFC = temp2[10]

    z.AvNGLostBarnN = temp2[11]
    z.AvNGLostBarnP = temp2[12]
    z.AvNGLostBarnFC = temp2[13]

    z.AvNGLostManP = temp2[14]

    # Average pathogen totals
    z.AvAnimalFC = temp2[15]
    z.AvWWOrgs = temp2[16]
    z.AvSSOrgs = temp2[17]
    z.AvUrbOrgs = temp2[18]
    z.AvWildOrgs = temp2[19]
    z.AvTotalOrgs = temp2[20]



@memoize
# @time_function
def AreaTotal(NRur, NUrb, Area):
    result = 0
    nlu = NLU_function(NRur, NUrb)
    for l in range(NRur):
        result += Area[l]
    for l in range(NRur, nlu):
        result += Area[l]
    return result

# @time_function
@memoize
def AreaTotal_2(Area):
    return np.sum(Area)

@memoize
def AttenN(AttenFlowDist, AttenFlowVel, AttenLossRateN):
    return FlowDays(AttenFlowDist, AttenFlowVel) * AttenLossRateN

# def AttenN_2():
#     pass



@memoize
def AvCN(NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area):
    result = 0
    urbareatotal = UrbAreaTotal(NRur, NUrb, Area)
    rurareatotal = RurAreaTotal(NRur, Area)
    areatotal = AreaTotal(NRur, NUrb, Area)
    avcnurb = AvCNUrb(NRur, NUrb, CNI_0, CNP_0, Imper, Area)
    avcnrur = AvCNRur(NRur, Area, CN)
    # Calculate the average CN
    if areatotal == 0:
        result += 0
    else:
        result += ((avcnrur * rurareatotal / areatotal) + (avcnurb * urbareatotal / areatotal))
    return result

# @time_function #vecotrized version was slower
# def AvCN_2(NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area):
#     # Calculate the average CN
#     areatotal = AreaTotal_2(Area)
#     if (areatotal > 0):
#         urbareatotal = UrbAreaTotal_2(NRur, NUrb, Area)
#         rurareatotal = RurAreaTotal_2(NRur, Area)
#
#         avcnurb = AvCNUrb_2(NRur, NUrb, CNI_0, CNP_0, Imper, Area)
#         avcnrur = AvCNRur_2(NRur, Area, CN)
#         return ((avcnrur * rurareatotal / areatotal) + (avcnurb * urbareatotal / areatotal))
#
#     else:
#         return 0



@memoize
def AvCNRur(NRur, Area, CN):
    result = 0
    rurareatotal = RurAreaTotal(NRur, Area)
    # Get the area weighted average CN for rural areas
    for l in range(NRur):
        # Calculate average area weighted CN and KF
        result += (CN[l] * Area[l] / rurareatotal) if rurareatotal > 0 else 0
    return result


def AvCNRur_2(NRur, Area, CN):
    rurareatotal = RurAreaTotal_2(NRur, Area)
    if (rurareatotal > 0):
        return np.sum(CN * Area / rurareatotal)
    else:
        return 0



# @time_function
@memoize
def AvCNUrb(NRur, NUrb, CNI_0, CNP_0, Imper, Area):
    result = 0
    nlu = NLU_function(NRur, NUrb)
    cni = CNI(NRur, NUrb, CNI_0)
    cnp = CNP(NRur, NUrb, CNP_0)
    urbareatotal = UrbAreaTotal(NRur, NUrb, Area)
    for l in range(NRur, nlu):
        # Calculate average area-weighted CN for urban areas
        if urbareatotal > 0:
            result += ((Imper[l] * cni[1][l] + (1 - Imper[l]) * cnp[1][l]) * Area[l] / urbareatotal)
    return result

# Tried, slower than original.
# @time_function
def AvCNUrb_2(NRur, NUrb, CNI_0, CNP_0, Imper, Area):
    result = 0
    nlu = NLU_function(NRur, NUrb)
    cni = CNI(NRur, NUrb, CNI_0)
    cnp = CNP(NRur, NUrb, CNP_0)
    urbareatotal = UrbAreaTotal(NRur, NUrb, Area)
    temp = ((Imper* cni[1] + (1 - Imper) * cnp[1]) * Area / urbareatotal)[NRur:]
    return np.sum(temp)




def AvErosion(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P):
    result = np.zeros(12)
    erosion = Erosion_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += erosion[Y][i] / NYrs
    return result


def AvErosion_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P):
    return np.sum(Erosion_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P), axis=0) / NYrs


@memoize
def AvEvapoTrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                 ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    result = np.zeros(12)
    evapotrans = Evapotrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper,
                            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += evapotrans[Y][i] / NYrs
    return result

@memoize
def AvEvapoTrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    evapotrans = Evapotrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    return np.average(evapotrans, axis=0)



def AvGroundWater(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                  AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap,
                  SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros(12)
    ground_wat_le = GroundWatLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs,
                                MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += ground_wat_le[Y][i] / NYrs
    return result


def AvGroundWater_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                    AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap,
                    SatStor_0, RecessionCoef, SeepCoef, Landuse, TileDrainDensity):
    return np.sum(GroundWatLE_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs,
                                MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Landuse, TileDrainDensity),
                  axis=0) / NYrs


def AvRunoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
             Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity):
    result = np.zeros(12)
    runoff = Runoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                    Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += runoff[Y][i] / NYrs
    return result

def AvRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
               Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity):
    return np.sum(Runoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                         Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity),
                  axis=0) / NYrs



@memoize
def AvSedYield(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
               Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
               StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
               AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
               Acoef, KF, LS, C, P, SedDelivRatio_0):
    result = np.zeros(12)
    sedyeild = SedYield_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                            Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap,
                            SatStor_0,
                            RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                            PointFlow,
                            StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                            AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85,
                            UrbBankStab,
                            Acoef, KF, LS, C, P, SedDelivRatio_0)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += sedyeild[Y][i] / NYrs
    return result


@memoize
def AvSedYield_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                 Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                 RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                 StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                 AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
                 Acoef, KF, LS, C, P, SedDelivRatio_0):
    return np.sum(
        SedYield_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                     Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                     RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                     StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                     AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
                     Acoef, KF, LS, C, P, SedDelivRatio_0),
        axis=0) / NYrs



def AvStreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                     Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                     GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                     SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab):
    result = np.zeros(12)
    stream_bank_eros_2 = StreamBankEros_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0,
                                          KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
                                          , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                          StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj,
                                          SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d,
                                          AgLength, n42, n45, n85, UrbBankStab)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += stream_bank_eros_2[Y][i] / NYrs
    return result


def AvStreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                       Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                       SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                       GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                       SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab):
    stream_bank_eros_2 = StreamBankEros_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0,
                                          KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
                                          , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                          StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj,
                                          SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d,
                                          AgLength, n42, n45, n85, UrbBankStab)
    return np.sum(stream_bank_eros_2, axis=0) / NYrs



def AvStreamBankN():
    pass


def AvStreamBankN_2():
    pass



def AvStreamBankNSum(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                     Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                     GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                     SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n54, n85, UrbBankStab, SedNitr,
                     BankNFrac, n69c, n45, n69):
    AvStreamBankN = np.zeros(12)
    for Y in range(NYrs):
        for i in range(12):
            AvStreamBankN[i] += \
                StreamBankN_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                              CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                              PointFlow, StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj,
                              SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                              UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69)[Y][i] / NYrs
    return sum(AvStreamBankN)


def AvStreamBankNSum_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                       Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                       SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                       GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                       SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n54, n85, UrbBankStab, SedNitr,
                       BankNFrac, n69c, n45, n69):
    return np.sum(StreamBankN_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                                  PointFlow, StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt,
                                  StreamFlowVolAdj,
                                  SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                                  UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69)) / NYrs



def AvTileDrain(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                Landuse, TileDrainDensity):
    result = np.zeros((12,))
    tile_drain = TileDrain(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                           Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                           RecessionCoef, SeepCoef, Landuse, TileDrainDensity)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += tile_drain[Y][i] / NYrs
    return result


def AvTileDrain_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                  Landuse, TileDrainDensity):
    return np.sum(
        TileDrain_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                    Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                    RecessionCoef, SeepCoef, Landuse, TileDrainDensity), axis=0)



def AvWithdrawal(NYrs, StreamWithdrawal, GroundWithdrawal):
    result = np.zeros(12)
    withdrawal = Withdrawal(NYrs, StreamWithdrawal, GroundWithdrawal)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += withdrawal[Y][i] / NYrs
    return result

@memoize
def AvWithdrawal_2(NYrs, StreamWithdrawal, GroundWithdrawal):
    return np.sum(Withdrawal_2(NYrs, StreamWithdrawal, GroundWithdrawal), axis=0) / NYrs


def BSed(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
         ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12))  # These used to be (NYrs,16) but it looks like a mistake
    sedtrans = SedTrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                        Imper,
                        ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = 0
            for m in range(i, 12):
                result[Y][i] = result[Y][i] + sedtrans[Y][m]
    return result

def BSed_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    sedtrans = SedTrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                        Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    return np.flip(np.cumsum(np.flip(sedtrans, axis=1), axis=1), axis=1)

# -*- coding: utf-8 -*-

"""
Imported from CalcLoads.bas
"""

# import logging


# log = logging.getLogger(__name__)



def CalculateLoads(z, Y):
    # PrecipitationTotal = 0
    # RunoffTotal = 0
    GroundWatLETotal = np.zeros(z.WxYrs)
    # EvapotransTotal = 0
    # PtSrcFlowTotal = 0
    # WithdrawalTotal = 0
    # StreamFlowTotal = 0
    SedYieldTotal = 0
    ErosionTotal = 0
    DisNitrTotal = 0
    DisPhosTotal = 0
    TotNitrTotal = 0
    TotPhosTotal = 0
    AnimalFCTotal = 0
    WWOrgsTotal = 0
    SSOrgsTotal = 0
    UrbOrgsTotal = 0
    WildOrgsTotal = 0
    TotalOrgsTotal = 0
    CMStreamTotal = 0
    OrgConcTotal = 0

    # ANNUAL WATER BALANCE CALCULATIONS
    for i in range(12):
        # Calculate landuse runoff for rural areas
        GroundWatLETotal += \
            GroundWatLE_1(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                          z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                          z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                          z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                          z.Landuse, z.TileDrainDensity)[Y][i]

    # CALCULATE ANNUAL NITROGEN  LOADS FROM NORMAL SEPTIC SYSTEMS
    AnNormNitr = 0
    for i in range(12):
        AnNormNitr += z.MonthNormNitr[i] * z.NumNormalSys[i]

    z.CalendarYr = z.WxYrBeg + (Y - 1)

    # SEDIMENT YIELD AND TILE DRAINAGE
    for i in range(12):
        SedYieldTotal += \
            SedYield_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.Acoef, z.NRur, z.KF, z.LS, z.C, z.P,
                       z.Area, z.NUrb, z.CNI_0, z.AntMoist_0, z.Grow_0, z.ISRR, z.ISRA, z.Qretention, z.PctAreaInfil,
                       z.n25b, z.CN, z.CNP_0, z.Imper, z.SedDelivRatio_0)[Y][i]
        ErosionTotal += \
            Erosion_1_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                        z.AntMoist_0,
                        z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs,
                        z.MaxWaterCap, z.SatStor_0,
                        z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
                        z.TileDrainDensity, z.PointFlow,
                        z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj,
                        z.SedAFactor_0,
                        z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength, z.n42,
                        z.n45, z.n85, z.UrbBankStab,
                        z.SedDelivRatio_0, z.Acoef, z.KF, z.LS, z.C, z.P)[Y][i]

        # CALCULATION OF THE LANDUSE EROSION AND SEDIMENT YIELDS
        for l in range(z.NRur):
            z.LuSedYield[Y][l] = \
                LuErosion_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.Acoef, z.KF, z.LS,
                            z.C, z.P, z.Area)[Y][l] * SedDelivRatio(z.SedDelivRatio_0)
            z.DisNitr[Y][i] += \
                nRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb, z.CN,
                          z.Grow_0,
                          z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth, z.LastManureMonth,
                          z.FirstManureMonth2, z.LastManureMonth2)[Y][i]
            z.DisPhos[Y][i] += \
                pRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb, z.CN,
                          z.Grow_0,
                          z.Area, z.PhosConc, z.ManuredAreas, z.FirstManureMonth, z.LastManureMonth, z.ManPhos,
                          z.FirstManureMonth2, z.LastManureMonth2)[Y][i]
            z.LuDisNitr[Y][l] += \
                nRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb, z.CN,
                          z.Grow_0,
                          z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth, z.LastManureMonth,
                          z.FirstManureMonth2, z.LastManureMonth2)[Y][i]
            z.LuDisPhos[Y][l] += \
                pRunoff_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb, z.CN,
                          z.Grow_0,
                          z.Area, z.PhosConc, z.ManuredAreas, z.FirstManureMonth, z.LastManureMonth, z.ManPhos,
                          z.FirstManureMonth2, z.LastManureMonth2)[Y][i]

        z.TotNitr[Y][i] = z.DisNitr[Y][i] + 0.001 * z.SedNitr * \
                          SedYield_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.Acoef, z.NRur, z.KF, z.LS,
                                     z.C, z.P,
                                     z.Area, z.NUrb, z.CNI_0, z.AntMoist_0, z.Grow_0, z.ISRR, z.ISRA, z.Qretention,
                                     z.PctAreaInfil,
                                     z.n25b, z.CN, z.CNP_0, z.Imper, z.SedDelivRatio_0)[Y][i]
        z.TotPhos[Y][i] = z.DisPhos[Y][i] + 0.001 * z.SedPhos * \
                          SedYield_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.Acoef, z.NRur, z.KF, z.LS,
                                     z.C, z.P,
                                     z.Area, z.NUrb, z.CNI_0, z.AntMoist_0, z.Grow_0, z.ISRR, z.ISRA, z.Qretention,
                                     z.PctAreaInfil,
                                     z.n25b, z.CN, z.CNP_0, z.Imper, z.SedDelivRatio_0)[Y][i]

        # SUM TILE DRAIN N, P, AND SEDIMENT
        z.TileDrainN[Y][i] += ((((TileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                              z.CNI_0,
                                              z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                              z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs,
                                              z.MaxWaterCap, z.SatStor_0,
                                              z.RecessionCoef, z.SeepCoef, z.Landuse,
                                              z.TileDrainDensity)[Y][i] / 100) * TotAreaMeters(z.NRur, z.NUrb,
                                                                                               z.Area)) * 1000) * z.TileNconc) / 1000000
        z.TileDrainP[Y][i] += ((((TileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                              z.CNI_0,
                                              z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                              z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs,
                                              z.MaxWaterCap, z.SatStor_0,
                                              z.RecessionCoef, z.SeepCoef, z.Landuse,
                                              z.TileDrainDensity)[Y][i] / 100) * TotAreaMeters(z.NRur, z.NUrb,
                                                                                               z.Area)) * 1000) * z.TilePConc) / 1000000
        z.TileDrainSed[Y][i] += ((((TileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb,
                                                z.Area, z.CNI_0,
                                                z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                                z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs,
                                                z.MaxWaterCap, z.SatStor_0,
                                                z.RecessionCoef, z.SeepCoef, z.Landuse,
                                                z.TileDrainDensity)[Y][i] / 100) * TotAreaMeters(z.NRur, z.NUrb,
                                                                                                 z.Area)) * 1000) * z.TileSedConc) / 1000000
        z.LuDisNitr[:, z.NRur:] += \
            LuDisLoad_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.Nqual, z.NRur, z.NUrb, z.Area, z.CNI_0,
                        z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.Qretention, z.PctAreaInfil,
                        z.LoadRateImp, z.LoadRatePerv, z.Storm, z.UrbBMPRed, z.DisFract,
                        z.FilterWidth, z.PctStrmBuf)[:, :, 0] / z.NYrs / 2
        z.LuDisPhos[:, z.NRur:] += \
            LuDisLoad_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.Nqual, z.NRur, z.NUrb, z.Area, z.CNI_0,
                        z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.Qretention, z.PctAreaInfil,
                        z.LoadRateImp, z.LoadRatePerv, z.Storm, z.UrbBMPRed, z.DisFract,
                        z.FilterWidth, z.PctStrmBuf)[:, :, 1] / z.NYrs / 2
        z.LuSedYield[:, z.NRur:] += (LuLoad_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                              z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA,
                                              z.Qretention, z.PctAreaInfil, z.Nqual, z.LoadRateImp, z.LoadRatePerv,
                                              z.Storm, z.UrbBMPRed,
                                              z.FilterWidth, z.PctStrmBuf)[:, :, 2] / z.NYrs) / 1000 / 2

        z.DisNitr[Y][i] += z.DisLoad[Y][i][0]
        z.DisPhos[Y][i] += z.DisLoad[Y][i][1]
        z.TotNitr[Y][i] += z.Load[Y][i][0]
        z.TotPhos[Y][i] += z.Load[Y][i][1]

        # ADD UPLAND N and P LOADS
        z.UplandN[Y][i] = z.TotNitr[Y][i]
        z.UplandP[Y][i] = z.TotPhos[Y][i]

        # ADD GROUNDWATER, POINT SOURCES,
        z.GroundNitr[Y][i] = 0.1 * z.GrNitrConc * \
                             GroundWatLE_1(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                           z.CNI_0,
                                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                           z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                           z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                           z.Landuse, z.TileDrainDensity)[Y][i] * AreaTotal_2(z.Area)
        z.GroundPhos[Y][i] = 0.1 * z.GrPhosConc * \
                             GroundWatLE_1(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                           z.CNI_0,
                                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                           z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                           z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                           z.Landuse, z.TileDrainDensity)[Y][i] * AreaTotal_2(z.Area)
        z.DisNitr[Y][i] += z.GroundNitr[Y][i] + z.PointNitr[i]
        z.DisPhos[Y][i] += z.GroundPhos[Y][i] + z.PointPhos[i]
        z.TotNitr[Y][i] += z.GroundNitr[Y][i] + z.PointNitr[i]
        z.TotPhos[Y][i] += z.GroundPhos[Y][i] + z.PointPhos[i]

        # ADD SEPTIC SYSTEM SOURCES TO MONTHLY DISSOLVED NUTRIENT TOTALS
        if GroundWatLETotal[Y] <= 0:
            GroundWatLETotal[Y] = 0.0001

        z.MonthNormNitr[i] = AnNormNitr * \
                             GroundWatLE_1(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                           z.CNI_0,
                                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                           z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                           z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                           z.Landuse, z.TileDrainDensity)[Y][i] / GroundWatLETotal[Y]

        z.DisSeptNitr = (z.MonthNormNitr[i]
                         + z.MonthPondNitr[i]
                         + z.MonthShortNitr[i] * z.NumShortSys[i]
                         + z.MonthDischargeNitr[i] * z.NumDischargeSys[i])

        z.DisSeptPhos = (z.MonthPondPhos[i]
                         + z.MonthShortPhos[i] * z.NumShortSys[i]
                         + z.MonthDischargePhos[i] * z.NumDischargeSys[i])

        # 0.59 IS ATTENUATION FACTOR FOR SOIL LOSS
        # 0.66 IS ATTENUATION FACTOR FOR SUBSURFACE FLOW LOSS
        z.DisSeptNitr = z.DisSeptNitr / 1000 * 0.59 * 0.66
        z.DisSeptPhos = z.DisSeptPhos / 1000

        z.DisNitr[Y][i] += z.DisSeptNitr
        z.DisPhos[Y][i] += z.DisSeptPhos
        z.TotNitr[Y][i] += z.DisSeptNitr
        z.TotPhos[Y][i] += z.DisSeptPhos
        z.SepticN[Y][i] += z.DisSeptNitr
        z.SepticP[Y][i] += z.DisSeptPhos

        # ANNUAL TOTALS
        DisNitrTotal += z.DisNitr[Y][i]
        DisPhosTotal += z.DisPhos[Y][i]
        TotNitrTotal += z.TotNitr[Y][i]
        TotPhosTotal += z.TotPhos[Y][i]

        # UPDATE ANNUAL SEPTIC SYSTEM LOADS
        z.SepticNitr[Y] += z.DisSeptNitr
        z.SepticPhos[Y] += z.DisSeptPhos

        # Annual pathogen totals
        AnimalFCTotal += z.AnimalFC[Y][i]
        WWOrgsTotal += z.WWOrgs[Y][i]
        SSOrgsTotal += z.SSOrgs[Y][i]
        UrbOrgsTotal += z.UrbOrgs[Y][i]
        WildOrgsTotal += z.WildOrgs[Y][i]
        TotalOrgsTotal += z.TotalOrgs[Y][i]
        CMStreamTotal += z.CMStream[Y][i]
        OrgConcTotal += z.OrgConc[Y][i]



@memoize
def CNI(NRur, NUrb, CNI_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    for l in range(NRur, nlu):
        result[0][l] = CNI_0[1][l] / (2.334 - 0.01334 * CNI_0[1][1])
        result[1][l] = CNI_0[1][l]
        result[2][l] = CNI_0[1][l] / (0.4036 + 0.0059 * CNI_0[1][l])
    return result

# @time_function
def CNI_2(NRur, NUrb, CNI_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    result[0] = CNI_0[1] / (2.334 - 0.01334 * CNI_0[1][1])
    result[1] = CNI_0[1]
    result[2] = CNI_0[1] / (0.4036 + 0.0059 * CNI_0[1])
    return result



@memoize
def CNP(NRur, NUrb, CNP_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    for l in range(NRur, nlu):
        result[0][l] = CNP_0[1][l] / (2.334 - 0.01334 * CNP_0[1][1])
        result[1][l] = CNP_0[1][l]
        result[2][l] = CNP_0[1][l] / (0.4036 + 0.0059 * CNP_0[1][l])
    return result

# @time_function
def CNP_2(NRur, NUrb, CNP_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    result[0] = CNP_0[1] / (2.334 - 0.01334 * CNP_0[1][1])
    result[1] = CNP_0[1]
    result[2] = CNP_0[1] / (0.4036 + 0.0059 * CNP_0[1])
    return result

try:
    from gwlfe_compiled import CNum_inner
except ImportError:
    print("Unable to import compiled CNum_inner, using slower version")
    from CNum_inner import CNum_inner


@memoize
# @time_function
def CNum(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, CN, NRur, NUrb, Grow_0):
    result = np.zeros((NYrs, 12, 31, 10))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec)  # I think this should be Melt_1
    grow_factor = GrowFactor(Grow_0)
    amc5 = AMC5(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)
    new_cn = NewCN(NRur, NUrb, CN)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                # result[Y][i][j][l] = 0
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        if CN[l] > 0:
                            if melt[Y][i][j] <= 0:
                                if grow_factor[i] > 0:
                                    # growing season
                                    if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 5.33:
                                        result[Y][i][j][l] = new_cn[2][l]
                                    elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 3.56:
                                        result[Y][i][j][l] = new_cn[0][l] + (
                                                CN[l] - new_cn[0][l]) * get_value_for_yesterday(amc5, 0, Y,
                                                                                                i, j,
                                                                                                NYrs,
                                                                                                DaysMonth) / 3.56
                                    else:
                                        result[Y][i][j][l] = CN[l] + (new_cn[2][l] - CN[l]) * (
                                                get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                        DaysMonth) - 3.56) / 1.77
                                else:
                                    # dormant season
                                    if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 2.79:
                                        result[Y][i][j][l] = new_cn[2][l]
                                    elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 1.27:
                                        result[Y][i][j][l] = new_cn[0][l] + (
                                                CN[l] - new_cn[0][l]) * get_value_for_yesterday(amc5, 0, Y,
                                                                                                i, j,
                                                                                                NYrs,
                                                                                                DaysMonth) / 1.27
                                    else:
                                        result[Y][i][j][l] = CN[l] + (new_cn[2][l] - CN[l]) * (
                                                get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                        DaysMonth) - 1.27) / 1.52
                            else:
                                result[Y][i][j][l] = new_cn[2][l]
                        # result[Y][i][j][l] = CNum
    return result


# @time_function
def CNum_1(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, CN, NRur, NUrb, Grow_0):
    melt_pest = np.repeat(Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], NRur, axis=3)
    newcn = NewCN_2(NRur, NUrb, CN)
    amc5 = np.repeat(AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)[:, :, :, None], NRur, axis=3)
    # g = GrowFactor(Grow_0)
    grow_factor = np.tile(GrowFactor(Grow_0)[None, :, None, None], (NYrs, 1, 31, NRur))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], NRur, axis=3)
    Temp = np.repeat(Temp[:, :, :, None], NRur, axis=3)
    CN_0 = np.tile(CN[:10][None, None, None, :], (NYrs, 12, 31, 1))
    newcn_0 = np.tile(newcn[0, :10][None, None, None, :], (NYrs, 12, 31, 1))
    newcn_2 = np.tile(newcn[2, :10][None, None, None, :], (NYrs, 12, 31, 1))
    result_0 = np.zeros((NYrs, 12, 31, NRur))
    result_1 = np.zeros((NYrs, 12, 31, NRur))
    result = np.zeros((NYrs, 12, 31, NRur))  # TODO: should we just generalize to NLU?
    # result[np.where((Temp > 0) & (water > 0.01) & (melt_pest <= 0) & (grow_factor>0))]
    result_0[np.where((Temp > 0) & (water > 0.01) & (CN_0 > 0))] = 1
    result_1[np.where((result_0 == 1) & (melt_pest <= 0) & (grow_factor > 0))] = 1
    result_1[np.where((result_0 == 1) & (melt_pest <= 0) & (grow_factor <= 0))] = 2
    result_1[np.where((result_0 == 1) & (melt_pest > 0))] = 3
    A = CN_0 + (newcn_2 - CN_0) * (amc5 - 3.56) / 1.77
    result[np.where((result_1 == 1))] = A[np.where((result_1 == 1))]
    result[np.where((result_1 == 1) & (amc5 >= 5.33))] = newcn_2[np.where((result_1 == 1) & (amc5 >= 5.33))]
    A = (newcn_0 + (CN_0 - newcn_0) * amc5 / 3.56)
    result[np.where((result_1 == 1) & (amc5 < 3.56))] = A[np.where((result_1 == 1) & (amc5 < 3.56))]
    A = CN_0 + (newcn_2 - CN_0) * (amc5 - 1.27) / 1.52
    result[np.where(result_1 == 2)] = A[np.where(result_1 == 2)]
    result[np.where((result_1 == 2) & (amc5 >= 2.79))] = newcn_2[np.where((result_1 == 2) & (amc5 >= 2.79))]
    A = newcn_0 + (CN_0 - newcn_0) * amc5 / 1.27
    result[np.where((result_1 == 2) & (amc5 < 1.27))] = A[np.where((result_1 == 2) & (amc5 < 1.27))]
    result[result_1 == 3] = newcn_2[result_1 == 3]
    return result


# CNUM_2 is faster than CNUM_1. CNUM_1 is
# @time_function
@memoize
def CNum_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, CN, NRur, NUrb, Grow_0):
    melt_pest = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    newcn = NewCN_2(NRur, NUrb, CN)
    amc5 = AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)
    grow_factor = GrowFactor_2(Grow_0)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    return CNum_inner(NYrs, DaysMonth, Temp, CN, NRur, melt_pest, newcn, amc5, grow_factor, water)


try:
    from gwlfe_compiled import CNumImperv_2_inner
except ImportError:
    print("Unable to import compiled CNumImper_2_inner, using slower version")
    from CNumImperv_2_inner import CNumImperv_2_inner


@memoize
def CNumImperv(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, Grow_0, AntMoist_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    cni = CNI(NRur, NUrb, CNI_0)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec)
    grow_factor = GrowFactor(Grow_0)
    amc5 = AMC5(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)

    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cni[1][l] > 0:
                                if melt[Y][i][j] <= 0:
                                    if grow_factor[i] > 0:
                                        # Growing season
                                        if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 5.33:
                                            result[Y][i][j][l] = cni[2][l]
                                        elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 3.56:
                                            result[Y][i][j][l] = cni[0][l] + (
                                                    cni[1][l] - cni[0][l]) * get_value_for_yesterday(amc5, 0, Y,
                                                                                                     i, j, NYrs,
                                                                                                     DaysMonth) / 3.56
                                        else:
                                            result[Y][i][j][l] = cni[1][l] + (cni[2][l] - cni[1][l]) * (
                                                    get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                            DaysMonth) - 3.56) / 1.77
                                    else:
                                        # Dormant season
                                        if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 2.79:
                                            result[Y][i][j][l] = cni[2][l]
                                        elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 1.27:
                                            result[Y][i][j][l] = cni[0][l] + (
                                                    cni[1][l] - cni[0][l]) * get_value_for_yesterday(amc5, 0, Y,
                                                                                                     i, j, NYrs,
                                                                                                     DaysMonth) / 1.27
                                        else:
                                            result[Y][i][j][l] = cni[1][l] + (cni[2][l] - cni[1][l]) * (
                                                    get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                            DaysMonth) - 1.27) / 1.52
                                else:
                                    result[Y][i][j][l] = cni[2][l]
    return result


def CNumImperv_2(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, Grow_0, AntMoist_0):
    nlu = NLU_function(NRur, NUrb)
    cni = CNI_2(NRur, NUrb, CNI_0)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    grow_factor = GrowFactor(Grow_0)
    amc5 = AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)
    return CNumImperv_2_inner(NYrs, NRur, DaysMonth, Temp, nlu, cni, water, melt, grow_factor, amc5)



@memoize
def CNumImpervReten(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNI_0,
                    Grow_0):  # TODO: this is exactly the same as perv and retention
    cni = CNI(NRur, NUrb, CNI_0)
    c_num_imperv = CNumImperv(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, Grow_0, AntMoist_0)
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:  # missing
                    if water[Y][i][j] < 0.05:  # missing
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cni[1][l] > 0:
                                result[Y][i][j][l] = 2540 / c_num_imperv[Y][i][j][l] - 25.4
                                if result[Y][i][j][l] < 0:
                                    result[Y][i][j][l] = 0
    return result


def CNumImpervReten_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNI_0, Grow_0):
    cni = CNI_2(NRur, NUrb, CNI_0)
    cni_1 = np.tile(cni[1][None, None, None, :], (NYrs, 12, 31, 1))
    c_num_imperv = CNumImperv_2(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, Grow_0, AntMoist_0)
    nlu = NLU_function(NRur, NUrb)
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], nlu, axis=3)
    result = np.zeros((NYrs, 12, 31, nlu))
    TempE = np.repeat(Temp[:, :, :, None], nlu, axis=3)
    result[np.where((TempE > 0) & (water >= 0.05) & (cni_1 > 0))] = 2540 / c_num_imperv[
        np.where((TempE > 0) & (water >= 0.05) & (cni_1 > 0))] - 25.4
    result[np.where(result < 0)] = 0
    return result


try:
    from gwlfe_compiled import CNumPerv_2_inner
except ImportError:
    print("Unable to import compiled CNumPerv_2_inner, using slower version")
    from CNumPerv_2_inner import CNumPerv_2_inner


@memoize
def CNumPerv(NYrs, DaysMonth, Temp, NRur, NUrb, CNP_0, InitSnow_0, Prec, Grow_0, AntMoist_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    cnp = CNP(NRur, NUrb, CNP_0)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec)
    grow_factor = GrowFactor(Grow_0)
    amc5 = AMC5(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)

    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cnp[1][l] > 0:
                                if melt[Y][i][j] <= 0:
                                    if grow_factor[i] > 0:
                                        # Growing season
                                        if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 5.33:
                                            result[Y][i][j][l] = cnp[2][l]
                                        elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 3.56:
                                            result[Y][i][j][l] = cnp[0][l] + (
                                                    cnp[1][l] - cnp[0][l]) * \
                                                                 get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                                         DaysMonth) / 3.56
                                        else:
                                            result[Y][i][j][l] = cnp[1][l] + (cnp[2][l] - cnp[1][l]) * (
                                                    get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                            DaysMonth) - 3.56) / 1.77
                                    else:
                                        # Dormant season
                                        if get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) >= 2.79:
                                            result[Y][i][j][l] = cnp[2][l]
                                        elif get_value_for_yesterday(amc5, 0, Y, i, j, NYrs, DaysMonth) < 1.27:
                                            result[Y][i][j][l] = cnp[0][l] + (
                                                    cnp[1][l] - cnp[0][l]) * \
                                                                 get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                                         DaysMonth) / 1.27
                                        else:
                                            result[Y][i][j][l] = cnp[1][l] + (cnp[2][l] - cnp[1][l]) * (
                                                    get_value_for_yesterday(amc5, 0, Y, i, j, NYrs,
                                                                            DaysMonth) - 1.27) / 1.52
                                else:
                                    result[Y][i][j][l] = cnp[2][l]
    return result


def CNumPerv_2(NYrs, DaysMonth, Temp, NRur, NUrb, CNP_0, InitSnow_0, Prec, Grow_0, AntMoist_0):
    nlu = NLU_function(NRur, NUrb)
    cnp = CNP_2(NRur, NUrb, CNP_0)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    grow_factor = GrowFactor(Grow_0)
    amc5 = AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)
    return CNumPerv_2_inner(NYrs, DaysMonth, Temp, NRur, nlu, cnp, water, melt, grow_factor, amc5)

# def CNumPerv_3(NYrs, DaysMonth, Temp, NRur, NUrb, CNP_0, InitSnow_0, Prec, Grow_0, AntMoist_0):
#     nlu = NLU(NRur, NUrb)
#     result = np.zeros((NYrs, 12, 31, 16))
#     landuse = np.zeros((16,))
#     cnp = CNP_2(NRur, NUrb, CNP_0)
#     water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
#     melt = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
#     grow_factor = GrowFactor(Grow_0)
#     amc5 = AMC5_yesterday(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0)
#
#     non_zero = result[(Temp > 0) & (water > 0.05)]
#
#     if amc5[Y][i][j] >= 5.33:
#         landuse[cnp[1] > 0] = cnp[2][l]
#     elif amc5[Y][i][j] < 3.56:
#         landuse[cnp[1] > 0] = cnp[0][l] + (
#                 cnp[1][l] - cnp[0][l]) * amc5[Y][i][j] / 3.56
#     else:
#         result[Y][i][j][l] = cnp[1][l] + (cnp[2][l] - cnp[1][l]) * (
#                 amc5[Y][i][j] - 3.56) / 1.77
#
#     # =
#     print(non_zero.shape)
#
#     temp = np.where(melt <= 0, 2, cnp[2])



@memoize
def CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNP_0, Grow_0):
    cnp = CNP(NRur, NUrb, CNP_0)
    c_num_perv = CNumPerv(NYrs, DaysMonth, Temp, NRur, NUrb, CNP_0, InitSnow_0, Prec, Grow_0, AntMoist_0)
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:  # missing
                    if water[Y][i][j] < 0.05:  # missing
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cnp[1][l] > 0:
                                result[Y][i][j][l] = 2540 / c_num_perv[Y][i][j][l] - 25.4
                                if result[Y][i][j][l] < 0:
                                    result[Y][i][j][l] = 0
    return result


def CNumPervReten_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNP_0, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    c_num_perv = CNumPerv_2(NYrs, DaysMonth, Temp, NRur, NUrb, CNP_0, InitSnow_0, Prec, Grow_0, AntMoist_0)
    cnp = CNP_2(NRur, NUrb, CNP_0)
    cnp_1 = np.tile(cnp[1][None, None, None, :], (NYrs, 12, 31, 1))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], nlu, axis=3)
    Temp = np.repeat(Temp[:, :, :, None], nlu, axis=3)
    result[np.where((Temp > 0) & (water >= 0.05) & (cnp_1 > 0))] = 2540 / c_num_perv[
        np.where((Temp > 0) & (water >= 0.05) & (cnp_1 > 0))] - 25.4
    result[np.where(result < 0)] = 0
    return result



leap_year = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             True, True, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, True, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, True, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, True, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, True, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False]
non_leap_year = [False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, True, True, True, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, True, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, True, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False, True,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False]


def mask_builder(DaysMonth):
    ones = np.ravel(np.ones((12, 31))).astype("int")
    slices = []
    for i, month in enumerate(DaysMonth[0]):
        slices.append(slice(31 * i, 31 * i + month))
    ones[np.r_[tuple(slices)]] = 0
    return ones


def ymd_to_daily(ymd_array, DaysMonth):
    month_maps = map(lambda x: leap_year if x[1] == 29 else non_leap_year, DaysMonth)
    mask = np.ravel(np.array(month_maps))
    x = ma.array(ymd_array, mask=mask)
    return x[~x.mask]


def daily_to_ymd(daily_array, NYrs, DaysMonth):
    result = np.zeros((NYrs * 12 * 31,))
    month_maps = map(lambda x: leap_year if x[1] == 29 else non_leap_year, DaysMonth)
    mask = np.ravel(np.array(month_maps))
    x = ma.array(result, mask=mask)
    x[~x.mask] = daily_array
    return x.reshape((NYrs, 12, 31))


def ymd_to_daily_slow(ymd_array, NYrs, DaysMonth):
    result = []
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result.append(ymd_array[Y][i][j])
    return np.array(result)


# @jit(cache=True, nopython=True)
def get_value_for_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday = variable_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday
                else:
                    yesterday = variable[Y][i][j]


# @jit(cache=True, nopython=True)
def get_value_for_yesterday_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday_yesterday = variable_0
    yesterday = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday_yesterday
                else:
                    yesterday_yesterday = yesterday
                    yesterday = variable[Y][i][j]


# @jit(cache=True, nopython=True)
def get_value_for_yesterday_yesterday_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday_yesterday_yesterday = variable_0
    yesterday_yesterday = 0
    yesterday = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday_yesterday_yesterday
                else:
                    yesterday_yesterday_yesterday = yesterday_yesterday
                    yesterday_yesterday = yesterday
                    yesterday = variable[Y][i][j]



@memoize
def DailyFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, Qretention, PctAreaInfil, n25b, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12, 31))
    day_runoff = DayRunoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                           AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    grflow = GrFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = day_runoff[Y][i][j] + grflow[Y][i][j]
    return result

@memoize
def DailyFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, Qretention, PctAreaInfil, n25b, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef):
    day_runoff = DayRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                           AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    grflow = GrFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    return day_runoff + grflow


# -*- coding: utf-8 -*-




class DataModel(object):
    def __init__(self, data=None):
        self.__dict__.update(self.defaults())
        self.__dict__.update(data or {})
        self.__dict__.update(self.date_guides())

    def defaults(self):
        NLU = 16
        NAnimals = 9

        return {
            'BasinId': 0,
            'AgSlope3to8': 0,
            'NumUAs': 0,
            'UABasinArea': 0,

            # Variables that are passed to PRedICT and are no longer used.
            'InName': '',
            'OutName': '',
            'UnitsFileFlag': 1,
            'AssessDate': '',
            'VersionNo': '',
            'ProjName': '',

            'NLU': NLU,
            'NAnimals': NAnimals,

            'Landuse': np.zeros(NLU, dtype=object),
            'Area': np.zeros(NLU),
            'CN': np.zeros(NLU),
            'KF': np.zeros(NLU),
            'LS': np.zeros(NLU),
            'C': np.zeros(NLU),
            'P': np.zeros(NLU),

            'NumNormalSys': np.zeros(12, dtype=int),
            'NumPondSys': np.zeros(12),
            'NumShortSys': np.zeros(12),
            'NumDischargeSys': np.zeros(12),
            'NumSewerSys': np.zeros(12),

            'SEDFEN': 0,
            'NFEN': 0,
            'PFEN': 0,

            'n86': 0,
            'n87': 0,
            'n88': 0,
            'n89': 0,
            'n90': 0,
            'n91': 0,
            'n92': 0,
            'n93': 0,
            'n94': 0,
            'n95': 0,
            'n95b': 0,
            'n95c': 0,
            'n95d': 0,
            'n95e': 0,

            'n96': 0,
            'n97': 0,
            'n98': 0,
            'n99': 0,
            'n99b': 0,
            'n99c': 0,
            'n99d': 0,
            'n99e': 0,
            'n100': 0,
            'n101': 0,
            'n101b': 0,
            'n101c': 0,
            'n101d': 0,
            'n101e': 0,
            'n102': 0,
            'n103a': 0,
            'n103b': 0,
            'n103c': 0,
            'n103d': 0,

            'n104': 0,
            'n105': 0,
            'n106': 0,
            'n106b': 0,
            'n106c': 0,
            'n106d': 0,
            'n107': 0,
            'n107b': 0,
            'n107c': 0,
            'n107d': 0,
            'n107e': 0,

            'Storm': 0,
            'CSNAreaSim': 0,
            'CSNDevType': 'None',
            # 'AdjUrbanQTotal': 0,
        }

    def date_guides(self):
        model = self.__dict__
        output = {}
        if 'WxYrBeg' in model and 'WxYrEnd' in model:
            begyear = model['WxYrBeg']
            endyear = model['WxYrEnd']
            year_range = endyear - begyear + 1
            month_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            if 'DaysMonth' not in model:
                output['DaysMonth'] = np.zeros((year_range, 12),
                                               dtype=np.int)
                for y in range(year_range):
                    year = begyear + y
                    for m in range(12):
                        output['DaysMonth'][y][m] = monthrange(year, m + 1)[1]

            if 'WxMonth' not in model:
                output['WxMonth'] = [month_abbr
                                     for y in range(year_range)]

            if 'WxYear' not in model:
                output['WxYear'] = [[begyear + y] * 12
                                    for y in range(year_range)]
        return output

    def __str__(self):
        return '<GWLF-E DataModel>'

    def tojson(self):
        return json.dumps(self.__dict__, cls=NumpyAwareJSONEncoder)


class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)



@memoize
def DayRunoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
              Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adj_q_total = AdjQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    q_total = QTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adj_q_total[Y][i][j] > 0:
                        result[Y][i][j] = adj_q_total[Y][i][j]
                    elif q_total[Y][i][j] > 0:
                        result[Y][i][j] = q_total[Y][i][j]
                    else:
                        result[Y][i][j] = 0
                else:
                    pass
    return result

@memoize
def DayRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
              Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12, 31))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adj_q_total = AdjQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    q_total = QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN)
    result[np.where((Temp>0) & (water > 0.01) & (adj_q_total > 0))]  = adj_q_total[np.where((Temp>0) & (water > 0) & (adj_q_total > 0))]
    result[np.where((Temp > 0) & (water > 0.01) & (q_total > 0))] = q_total[np.where((Temp > 0) & (water > 0) & (q_total > 0))]
    return result

try:
    from gwlfe_compiled import DeepSeep_inner
except ImportError:
    print("Unable to import compiled DeepSeep_inner, using slower version")
    from DeepSeep_inner import DeepSeep_inner



@memoize
def DeepSeep(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12, 31))
    grflow = np.zeros((NYrs, 12, 31))
    satstor = np.zeros((NYrs, 12, 31))
    percolation = Percolation(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    satstor_carryover = SatStor_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satstor[Y][i][j] = satstor_carryover
                grflow[Y][i][j] = RecessionCoef * satstor[Y][i][j]
                result[Y][i][j] = SeepCoef * satstor[Y][i][j]
                satstor[Y][i][j] = satstor[Y][i][j] + percolation[Y][i][j] - grflow[Y][i][j] - result[Y][i][j]
                if satstor[Y][i][j] < 0:
                    satstor[Y][i][j] = 0
                satstor_carryover = satstor[Y][i][j]
    return result

# @memoize
def DeepSeep_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
               ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    percolation = Percolation_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    return DeepSeep_inner(NYrs, SatStor_0, DaysMonth, RecessionCoef, SeepCoef, percolation)[0]


@memoize
def DisLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                        SweepFrac, UrbSweepFrac, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 3))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    netdisload = NetDisLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                        SweepFrac, UrbSweepFrac, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for q in range(Nqual):
                        result[Y][i][q] += netdisload[Y][i][j][q]
                        if result[Y][i][q] < 0:
                            result[Y][i][q] = 0
                else:
                    pass
    return result


def DisLoad_2():
    pass



@memoize
def DisSurfLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm,
                UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 31, 16, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0,
                                        Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    surfaceload = SurfaceLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                              CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv,
                              Storm, UrbBMPRed)
    retentioneff = RetentionEff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0,
                                AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, PctAreaInfil)
    filtereff = FilterEff(FilterWidth)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][i][j][l][q] = DisFract[l][q] * surfaceload[Y][i][j][l][q]
                                result[Y][i][j][l][q] *= (1 - retentioneff) * (1 - (filtereff * PctStrmBuf))
                    else:
                        pass
                else:
                    pass
    return result


def DisSurfLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                  Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv,
                  Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu - NRur, Nqual))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                          Grow_0, CNP_0,
                                          Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    surfaceload = SurfaceLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm,
                                UrbBMPRed)
    retentioneff = RetentionEff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0,
                                  AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, PctAreaInfil)
    filtereff = FilterEff_2(FilterWidth)
    nonzero = np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001))
    result[nonzero] = surfaceload[nonzero] * DisFract[NRur:] * (1 - retentioneff) * (1 - (filtereff * PctStrmBuf))
    return result

# -*- coding: utf-8 -*-
# from numba import jit

class YesOrNo(object):
    NO = '<No>'
    YES = '<Yes>'

    @classmethod
    def parse(cls, value):
        if value in ('0', 'N'):
            return cls.NO
        elif value in ('1', 'Y'):
            return cls.YES
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def intval(cls, value):
        if value == cls.NO:
            return 0
        elif value == cls.YES:
            return 1
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def gmsval(cls, value):
        if value == cls.NO:
            return 'N'
        elif value == cls.YES:
            return 'Y'
        raise ValueError('Unexpected value: ' + str(value))


class ETflag(object):
    HAMON_METHOD = '<Hamon method>'
    BLAINY_CRIDDLE_METHOD = '<Blainy-Criddle method>'

    @classmethod
    def parse(cls, value):
        value = int(value)
        if value == 0:
            return cls.HAMON_METHOD
        elif value == 1:
            return cls.BLAINY_CRIDDLE_METHOD
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def gmsval(cls, value):
        if value == cls.HAMON_METHOD:
            return 0
        elif value == cls.BLAINY_CRIDDLE_METHOD:
            return 1
        raise ValueError('Unexpected value: ' + str(value))

GROWING_SEASON = '<Growing season>'
class GrowFlag(object):
    NON_GROWING_SEASON = '<Non-growing season>'
    GROWING_SEASON = '<Growing season>'

    @classmethod
    def parse(cls, value):
        value = int(value)
        if value == 0:
            return cls.NON_GROWING_SEASON
        elif value == 1:
            return cls.GROWING_SEASON
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    # @jit(cache=True, nopython=True)
    def intval(cls, value):
        if value == cls.NON_GROWING_SEASON:
            return 0
        elif value == cls.GROWING_SEASON:
            return 1
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def gmsval(cls, value):
        return cls.intval(value)


class SweepType(object):
    VACUUM = '<Vacuum>'
    MECHANICAL = '<Mechanical>'

    @classmethod
    def parse(cls, value):
        value = int(value)
        if value == 1:
            return cls.MECHANICAL
        elif value == 2:
            return cls.VACUUM
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def gmsval(cls, value):
        if value == cls.MECHANICAL:
            return 1
        elif value == cls.VACUUM:
            return 2
        raise ValueError('Unexpected value: ' + str(value))


# TODO: Use actual NLCD values
# Reference: https://drive.google.com/a/azavea.com/file/d/0B3v0QxIOuR_nX3Rnekp0NGUyOGM/view
class LandUse(object):
    WATER = '<Water>'
    HAY_PAST = '<Hay/Past>'
    CROPLAND = '<Cropland>'
    FOREST = '<Forest>'
    WETLAND = '<Wetland>'
    DISTURBED = '<Disturbed>'
    TURFGRASS = '<Turfgrass>'
    OPEN_LAND = '<Open_Land>'
    BARE_ROCK = '<Bare_Rock>'
    SANDY_AREAS = '<Sandy_Areas>'
    UNPAVED_ROAD = '<Unpaved_Road>'
    LD_MIXED = '<Ld_Mixed>'
    MD_MIXED = '<Md_Mixed>'
    HD_MIXED = '<Hd_Mixed>'
    LD_RESIDENTIAL = '<Ld_Residential>'
    MD_RESIDENTIAL = '<Md_Residential>'
    HD_RESIDENTIAL = '<Hd_Residential>'

    @classmethod
    def parse(cls, value):
        if value == 'Water':
            return cls.WATER
        if value in ('Hay/Past', 'Hay'):
            return cls.HAY_PAST
        elif value == 'Cropland':
            return cls.CROPLAND
        elif value == 'Forest':
            return cls.FOREST
        elif value == 'Wetland':
            return cls.WETLAND
        elif value in ('Disturbed', 'Disturbed Land'):
            return cls.DISTURBED
        elif value == 'Turfgrass':
            return cls.TURFGRASS
        elif value in ('Open_Land', 'Open Land'):
            return cls.OPEN_LAND
        elif value in ('Bare_Rock', 'Bare Rock'):
            return cls.BARE_ROCK
        elif value in ('Sandy_Areas', 'Sandy Areas'):
            return cls.SANDY_AREAS
        elif value in ('Unpaved_Road', 'Unpaved Roads'):
            return cls.UNPAVED_ROAD
        elif value in ('Ld_Mixed', 'LD Mixed'):
            return cls.LD_MIXED
        elif value in ('Md_Mixed', 'MD Mixed'):
            return cls.MD_MIXED
        elif value in ('Hd_Mixed', 'HD Mixed'):
            return cls.HD_MIXED
        elif value in ('Ld_Residential', 'LD Residential'):
            return cls.LD_RESIDENTIAL
        elif value in ('Md_Residential', 'MD Residential'):
            return cls.MD_RESIDENTIAL
        elif value in ('Hd_Residential', 'HD Residential'):
            return cls.HD_RESIDENTIAL
        raise ValueError('Unexpected value: ' + str(value))

    @classmethod
    def gmsval(cls, value):
        if value == cls.WATER:
            return 'Water'
        elif value == cls.HAY_PAST:
            return 'Hay/Past'
        elif value == cls.CROPLAND:
            return 'Cropland'
        elif value == cls.FOREST:
            return 'Forest'
        elif value == cls.WETLAND:
            return 'Wetland'
        elif value == cls.DISTURBED:
            return 'Disturbed'
        elif value == cls.TURFGRASS:
            return 'Turfgrass'
        elif value == cls.OPEN_LAND:
            return 'Open_Land'
        elif value == cls.BARE_ROCK:
            return 'Bare_Rock'
        elif value == cls.SANDY_AREAS:
            return 'Sandy_Areas'
        elif value == cls.UNPAVED_ROAD:
            return 'Unpaved_Road'
        elif value == cls.LD_MIXED:
            return 'Ld_Mixed'
        elif value == cls.MD_MIXED:
            return 'Md_Mixed'
        elif value == cls.HD_MIXED:
            return 'Hd_Mixed'
        elif value == cls.LD_RESIDENTIAL:
            return 'Ld_Residential'
        elif value == cls.MD_RESIDENTIAL:
            return 'Md_Residential'
        elif value == cls.HD_RESIDENTIAL:
            return 'Hd_Residential'
        raise ValueError('Unexpected value: ' + str(value))



@memoize
def Erosion(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area):
    result = np.zeros((NYrs, 12))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rureros = RurEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                        result[Y][i] = result[Y][i] + rureros[Y][i][j][l]
                    else:
                        pass
    return result


@memoize
def Erosion_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area):
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rureros = RurEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    # return np.sum(np.where((Temp > 0) & (water > 0.01), np.sum(rureros, axis=3), 0), axis=2)
    return np.sum(np.sum(rureros, axis=3), axis=2)


@memoize
def ErosionSedYield(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area, SedDelivRatio_0,
                    NUrb, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN,
                    UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                    Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                    NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength,
                    n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab):
    erosion = np.zeros((NYrs, 12))
    sedyield = np.zeros((NYrs, 12))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rureros = RurEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    bsed = BSed(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    seddelivratio = SedDelivRatio(SedDelivRatio_0)
    sedtrans = SedTrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                        Imper,
                        ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    streambankeros_2 = StreamBankEros_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs,
                                        MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b,
                                        Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal
                                        , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                        SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85,
                                        UrbBankStab)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                        erosion[Y][i] = erosion[Y][i] + rureros[Y][i][j][l]
                    else:
                        pass
            for m in range(i + 1):
                if bsed[Y][m] > 0:
                    sedyield[Y][i] += erosion[Y][m] / bsed[Y][m]
            sedyield[Y][i] = seddelivratio * sedtrans[Y][i] * sedyield[Y][i]
            # TODO These are now used to calculate: SedYieldTotal, ErosionTotal, TotalNitr, and TotalPhos
        for i in range(12):
            sedyield[Y][i] += streambankeros_2[Y][i] / 1000
            if seddelivratio > 0 and erosion[Y][i] < sedyield[Y][i]:
                erosion[Y][i] = sedyield[Y][i] / seddelivratio
            # TODO Now calculated is: AvSedYield, ErosSum, and AvErosion
    pass


def ErosionSedYield_2():
    pass



@memoize
def Erosion_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P):
    result = np.zeros((NYrs, 12))
    seddelivratio = SedDelivRatio(SedDelivRatio_0)
    erosion = Erosion(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    sedyield = SedYield_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                          Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                          StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                          AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85,
                          UrbBankStab, Acoef, KF, LS, C, P, SedDelivRatio_0)
    for Y in range(NYrs):
        for i in range(12):
            if seddelivratio > 0 and erosion[Y][i] < sedyield[Y][i]:
                result[Y][i] = sedyield[Y][i] / seddelivratio
            else:
                result[Y][i] = erosion[Y][i]
    return result

@memoize
def Erosion_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
              AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
              SedDelivRatio_0, Acoef, KF, LS, C, P):
    seddelivratio = np.resize(SedDelivRatio(SedDelivRatio_0),(NYrs,12))
    erosion = Erosion_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    sedyield = SedYield_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                          Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                          StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                          AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85,
                          UrbBankStab, Acoef, KF, LS, C, P, SedDelivRatio_0)
    return np.where((seddelivratio > 0) & (erosion < sedyield),sedyield / seddelivratio,erosion)


@memoize
def Erosiv(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef):
    result = np.zeros((NYrs, 12, 31))
    init_snow = InitSnow(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    init_snow_yesterday = InitSnow_0
    rain = Rain(NYrs, DaysMonth, Temp, Prec)
    melt_1 = Melt_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0:
                    if (init_snow_yesterday > 0.001):
                        if rain[Y][i][j] > 0 and init_snow_yesterday - melt_1[Y][i][j] < 0.001:
                            result[Y][i][j] = 6.46 * Acoef[i] * rain[Y][i][j] ** 1.81
                    else:
                        if rain[Y][i][j] > 0 and init_snow_yesterday < 0.001:
                            result[Y][i][j] = 6.46 * Acoef[i] * rain[Y][i][j] ** 1.81
                init_snow_yesterday = init_snow[Y][i][j]
    return result

def Erosiv_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef):
    result = np.zeros((NYrs, 12, 31))
    rain = Rain_2(Temp, Prec)
    init_snow_yesterday = InitSnowYesterday(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt_1 = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    erosiv = 6.46*Acoef.reshape((12,1)) *rain **1.81
    result[np.where((Temp>0) & (init_snow_yesterday > 0.001) & (rain > 0 ) & (init_snow_yesterday - melt_1 < 0.001))] = erosiv[np.where((Temp>0) & (init_snow_yesterday > 0.001) & (rain > 0 ) & (init_snow_yesterday - melt_1 < 0.001))]
    result[np.where((Temp>0) & (init_snow_yesterday <= 0.001) & (rain > 0 ))] =erosiv[np.where((Temp>0) & (init_snow_yesterday <= 0.001) & (rain > 0 ))]
    return result


@memoize
def ErosSum(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
            AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET,
            DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil,
            n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
            NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
            StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
            SedDelivRatio_0, Acoef, KF, LS, C, P):
    result = np.zeros((NYrs,))
    for Y in range(NYrs):
        result[Y] = 0
        for i in range(12):
            result[Y] += Erosion_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                   AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET,
                                   DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil,
                                   n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                   NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                                   StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
                                   SedDelivRatio_0, Acoef, KF, LS, C, P)[Y][i]


    return result

# @time_function
@memoize
def ErosSum_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
            AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET,
            DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil,
            n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
            NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
            StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
            SedDelivRatio_0, Acoef, KF, LS, C, P):
    return np.sum(Erosion_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                   AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET,
                                   DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil,
                                   n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                   NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                                   StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
                                   SedDelivRatio_0, Acoef, KF, LS, C, P),axis=1)



@memoize
def ErosWashoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Acoef, KF, LS, C, P, Area):
    result = np.zeros((NYrs, 16, 12))
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rureros = RurEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(nlu):
                result[Y, l, i] = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        result[Y][l][i] = result[Y][l][i] + rureros[Y][i][j][l]
                else:
                    pass
    return result

@memoize
def ErosWashoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, Acoef, KF, LS, C, P, Area):
    return np.sum(RurEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area), axis=2)



@memoize
def ET_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
         ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    result = np.zeros((NYrs, 12, 31))
    infiltration = Infiltration_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN)
    unsatstor_carryover = UnsatStor_0
    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = unsatstor_carryover
                result[Y][i][j] = result[Y][i][j] + infiltration[Y][i][j]
                if et[Y][i][j] >= result[Y][i][j]:
                    et[Y][i][j] = result[Y][i][j]
                    result[Y][i][j] = 0
                else:
                    result[Y][i][j] = result[Y][i][j] - et[Y][i][j]
                if result[Y][i][j] > MaxWaterCap:
                    result[Y][i][j] = MaxWaterCap
                else:
                    pass
                unsatstor_carryover = result[Y][i][j]
    return et


def ET_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    infiltration = Infiltration_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN)
    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    return UnsatStor_inner(NYrs, DaysMonth, MaxWaterCap, UnsatStor_0, infiltration, et)[1]


@memoize
def Evapotrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
               ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    result = np.zeros((NYrs, 12))
    et_2 = ET_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + et_2[Y][i][j]
    return result

@memoize
def Evapotrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    et_2 = ET_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    return np.sum(et_2,axis=2)



@memoize
def FilterEff(FilterWidth):
    if FilterWidth <= 30:
        result = FilterWidth / 30
    else:
        result = 1
    return result


#Both have same running time
@memoize
def FilterEff_2(FilterWidth):
    result = 1
    if FilterWidth <= 30:
        result = FilterWidth / 30
    return result


# @memoize
def Flow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
         ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12, 31))
    qtotal = QTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN)
    grflow = GrFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = qtotal[Y][i][j] + grflow[Y][i][j]
    return result


def Flow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    qtotal = QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN)
    grflow = GrFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    return qtotal + grflow


@memoize
def FlowDays(AttenFlowDist, AttenFlowVel):
    if AttenFlowDist > 0 and AttenFlowVel > 0:
        return AttenFlowDist / (AttenFlowVel * 24)
    else:
        return 0


# def FlowDays_2():
#     pass



def GrazingAnimal(GrazingAnimal_0):
    return GrazingAnimal_0


def GrazingAnimal_2(GrazingAnimal_0):
    return GrazingAnimal_0 == YesOrNo.YES



@memoize
def GrFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12, 31))
    deepseep = np.zeros((NYrs, 12, 31))
    satstor = np.zeros((NYrs, 12, 31))
    percolation = Percolation(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    satstor_carryover = SatStor_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satstor[Y][i][j] = satstor_carryover
                result[Y][i][j] = RecessionCoef * satstor[Y][i][j]
                deepseep[Y][i][j] = SeepCoef * satstor[Y][i][j]
                satstor[Y][i][j] = satstor[Y][i][j] + percolation[Y][i][j] - result[Y][i][j] - deepseep[Y][i][j]
                if satstor[Y][i][j] < 0:
                    satstor[Y][i][j] = 0
                satstor_carryover = satstor[Y][i][j]
    return result


# @jit(cache=True, nopython=True)#using deep seep inner because the calculations are linked
# def GrFlow_inner(NYrs, SatStor_0, DaysMonth, RecessionCoef, SeepCoef, percolation):
#     result = np.zeros((NYrs, 12, 31))
#     satstor_carryover = SatStor_0
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 result[Y][i][j] = RecessionCoef * satstor_carryover
#                 satstor_carryover = satstor_carryover + percolation[Y][i][j] - result[Y][i][j] - SeepCoef * \
#                                     satstor_carryover
#                 if satstor_carryover < 0:
#                     satstor_carryover = 0
#     return result


def GrFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    percolation = Percolation_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)

    return DeepSeep_inner(NYrs, SatStor_0, DaysMonth, RecessionCoef, SeepCoef, percolation)[1]



@memoize
def GroundWatLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12))
    grflow = GrFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + grflow[Y][i][j]
    return result

@memoize
def GroundWatLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    grflow = GrFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    return np.sum(grflow, axis=2)

# THIS IS A FUNCTION THAT FULLY SATISFIES GroundWatLE and matches the original model output. NOTHING IS SEPARATED YET
# def GroundWatLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
#            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Landuse, TileDrainDensity):
#     result = np.zeros((NYrs, 12))
#     areatotal = AreaTotal(NRur, NUrb, Area) #4129.0
#     agareatotal = AgAreaTotal(NRur, Landuse, Area) # 2499.0
#     grflow = GrFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
#            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
#     gwagle = np.zeros((NYrs, 12))
#     tiledraingw = np.zeros((NYrs, 12))
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 result[Y][i] = result[Y][i] + grflow[Y][i][j]
#             if areatotal > 0:
#                 gwagle[Y][i] = (gwagle[Y][i] + (result[Y][i] * (agareatotal / areatotal)))
#             tiledraingw[Y][i] = (tiledraingw[Y][i] + [gwagle[Y][i] * TileDrainDensity])
#             result[Y][i] = result[Y][i] - tiledraingw[Y][i]
#             if result[Y][i] < 0:
#                 result[Y][i] = 0
#     #return result
#     pass



@memoize
def GroundWatLE_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                  Landuse, TileDrainDensity):
    result = np.zeros((NYrs, 12))
    tiledraingw = TileDrainGW_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                              SeepCoef, Landuse, TileDrainDensity)
    grounwatle_1 = GroundWatLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                               CNP_0, Imper,
                               ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                               SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = grounwatle_1[Y][i] - tiledraingw[Y][i]
        if result[Y][i] < 0:
            result[Y][i] = 0
    return result


def GroundWatLE_1_2():
    pass



def Grow(Grow_0):
    return Grow_0


def Grow_2(Grow_0):
    return Grow_0 == GROWING_SEASON


# @time_function


@memoize
def GrowFactor(Grow_0):
    result = np.zeros((12,))
    for i in range(12):
        result[i] = Grow_0[i] == GROWING_SEASON  # TODO: seems like there is some inefficency left in Grow_0
    return result


@memoize
def GrowFactor_2(Grow_0):
    return Grow_2(Grow_0)


@memoize
def GwAgLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Landuse):
    result = np.zeros((NYrs, 12))
    areatotal = AreaTotal(NRur, NUrb, Area)
    agareatotal = AgAreaTotal(NRur, Landuse, Area)
    groundwatle = GroundWatLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper,
                              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                              SeepCoef)
    for Y in range(NYrs):
        for i in range(12):
            if areatotal > 0:
                result[Y][i] = (result[Y][i] + (groundwatle[Y][i] * (agareatotal / areatotal)))
    return result


def GwAgLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Landuse):
    areatotal = AreaTotal_2(Area)
    agareatotal = AgAreaTotal(NRur, Landuse, Area)
    groundwatle = GroundWatLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                RecessionCoef, SeepCoef)
    if (areatotal > 0):
        return groundwatle * agareatotal / areatotal
    else:
        return np.zeros((NYrs, 12))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runs the GWLF-E MapShed model.

Imported from GWLF-E.frm
"""
# from numba import jit



log = logging.getLogger(__name__)


# @time_function
# @jit()
def run(z):
    log.debug('Running model...')

    # Raise exception instead of printing a warning for floating point
    # overflow, underflow, and division by 0 errors.
    np.seterr(all='raise')

    # MODEL CALCULATIONS FOR EACH YEAR OF ANALYSIS - WATER BALANCE,
    # NUTRIENTS AND SEDIMENT LOADS
    ReadAllData(z)

    # --------- run the remaining parts of the model ---------------------

    z.LuTotNitr[:, :z.NRur] = LuTotNitr_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur,
                                          z.NUrb, z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas,
                                          z.FirstManureMonth, z.LastManureMonth, z.FirstManureMonth2,
                                          z.LastManureMonth2, z.SedDelivRatio_0, z.KF, z.LS, z.C,
                                          z.P, z.SedNitr, z.Acoef)

    z.LuTotPhos[:, :z.NRur] = LuTotPhos_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur,
                                          z.NUrb, z.CN, z.Grow_0, z.Area, z.PhosConc, z.ManPhos,
                                          z.ManuredAreas, z.FirstManureMonth, z.LastManureMonth, z.FirstManureMonth2,
                                          z.LastManureMonth2, z.SedDelivRatio_0,
                                          z.KF, z.LS, z.C, z.P, z.Acoef, z.SedPhos)
    # CALCLULATE PRELIMINARY INITIALIZATIONS AND VALUES FOR
    # WATER BALANCE AND NUTRIENTS
    InitialCalculations(z)

    for Y in range(z.NYrs):
        # Initialize monthly septic system variables
        z.MonthPondNitr = np.zeros(12)
        z.MonthPondPhos = np.zeros(12)
        z.MonthNormNitr = np.zeros(12)
        z.MonthShortNitr = np.zeros(12)
        z.MonthShortPhos = np.zeros(12)
        z.MonthDischargeNitr = np.zeros(12)
        z.MonthDischargePhos = np.zeros(12)

        # FOR EACH MONTH...
        for i in range(12):
            # LOOP THROUGH NUMBER OF LANDUSES IN THE BASIN TO GET QRUNOFF
            for l in range(z.NLU):
                z.QRunoff[l, i] = 0
                z.AgQRunoff[l, i] = 0
                # z.ErosWashoff[l, i] = 0
                # z.RurQRunoff[l, i] = 0
                # z.UrbQRunoff[l, i] = 0
                # z.LuErosion[Y, l] = 0

            # DAILY CALCULATIONS
            for j in range(z.DaysMonth[Y][i]):
                # ***** END WEATHER DATA ANALYSIS *****

                # ***** WATERSHED WATER BALANCE *****

                z.PondNitrLoad = (z.NumPondSys[i] *
                                  (z.NitrSepticLoad - z.NitrPlantUptake * GrowFactor_2(z.Grow_0)[i]))
                z.PondPhosLoad = (z.NumPondSys[i] *
                                  (z.PhosSepticLoad - z.PhosPlantUptake * GrowFactor_2(z.Grow_0)[i]))

                # UPDATE MASS BALANCE ON PONDED EFFLUENT
                if (z.Temp[Y][i][j] <= 0 or InitSnow_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec)[Y][i][j] > 0):

                    # ALL INPUTS GO TO FROZEN STORAGE
                    z.FrozenPondNitr = z.FrozenPondNitr + z.PondNitrLoad
                    z.FrozenPondPhos = z.FrozenPondPhos + z.PondPhosLoad

                    # NO NUTIENT OVERFLOW
                    z.NitrPondOverflow = 0
                    z.PhosPondOverflow = 0
                else:
                    z.NitrPondOverflow = z.FrozenPondNitr + z.PondNitrLoad
                    z.PhosPondOverflow = z.FrozenPondPhos + z.PondPhosLoad
                    z.FrozenPondNitr = 0
                    z.FrozenPondPhos = 0

                # Obtain the monthly Pond nutrients
                z.MonthPondNitr[i] = z.MonthPondNitr[i] + z.NitrPondOverflow
                z.MonthPondPhos[i] = z.MonthPondPhos[i] + z.PhosPondOverflow

                # grow_factor = GrowFlag.intval(z.Grow_0[i]) # duplicate

                # Obtain the monthly Normal Nitrogen
                z.MonthNormNitr[i] = (z.MonthNormNitr[i] + z.NitrSepticLoad -
                                      z.NitrPlantUptake * GrowFactor_2(z.Grow_0)[i])

                # 0.56 IS ATTENUATION FACTOR FOR SOIL LOSS
                # 0.66 IS ATTENUATION FACTOR FOR SUBSURFACE FLOW LOSS
                z.MonthShortNitr[i] = (z.MonthShortNitr[i] + z.NitrSepticLoad -
                                       z.NitrPlantUptake * GrowFactor_2(z.Grow_0)[i])
                z.MonthShortPhos[i] = (z.MonthShortPhos[i] + z.PhosSepticLoad -
                                       z.PhosPlantUptake * GrowFactor_2(z.Grow_0)[i])
                z.MonthDischargeNitr[i] = z.MonthDischargeNitr[i] + z.NitrSepticLoad
                z.MonthDischargePhos[i] = z.MonthDischargePhos[i] + z.PhosSepticLoad

        # CALCULATE ANIMAL FEEDING OPERATIONS OUTPUT
        AnimalOperations(z, Y)

        # CALCULATE NUTRIENT AND SEDIMENT LOADS
        CalculateLoads(z, Y)

        # CALCULATE STREAM BANK EROSION
        CalculateStreamBankEros(z, Y)

        # CALCULATE FINAL ANNUAL MEAN LOADS
        CalculateAnnualMeanLoads(z, Y)

    # CALCULATE FINAL MONTHLY AND ANNUAL WATER BALANCE FOR
    # AVERAGE STREAM FLOW

    for i in range(12):
        z.AvStreamFlow[i] = (
                AvRunoff_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.Qretention, z.PctAreaInfil,
                           z.n25b, z.CN, z.Landuse, z.TileDrainDensity)[i] +
                AvGroundWater_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                                z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                                z.PcntET, z.DayHrs, z.MaxWaterCap,
                                z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Landuse, z.TileDrainDensity)[i] +
                z.AvPtSrcFlow[i] +
                AvTileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                              z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                              z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                              z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                              z.Landuse, z.TileDrainDensity)[i] -
                AvWithdrawal_2(z.NYrs, z.StreamWithdrawal, z.GroundWithdrawal)[i])

        z.AvCMStream[i] = (z.AvStreamFlow[i] / 100) * TotAreaMeters(z.NRur, z.NUrb, z.Area)
        if z.AvCMStream[i] > 0:
            z.AvOrgConc[i] = (z.AvTotalOrgs[i] / (z.AvCMStream[i] * 1000)) / 10
        else:
            z.AvOrgConc[i] = 0
    z.AvOrgConc[0] = 0

    z.AvStreamFlowSum = (z.AvRunoffSum + z.AvGroundWaterSum +
                         z.AvPtSrcFlowSum + z.AvTileDrainSum -
                         z.AvWithdrawalSum)

    log.debug("Model run complete for " + str(z.NYrs) + " years of data.")

    output = WriteOutput(z)
    # WriteOutputFiles.WriteOutputSumFiles()
    return output


class HashableArray(np.ndarray):
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        obj.hash = randint(100, 999)
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.hash = getattr(obj, 'info', None)

    def __hash__(self):
        return self.hash

    def __repr__(self):
        return str(self.hash)

    # def __getitem__(self, item):
    #     # print(self.name + "[" + str(item) + "]")
    #     attr = np.ndarray.__getitem__(self, item)
    #     if issubclass(type(attr), np.ndarray):  # handle multi dimensional arrays
    #         return ArraySpy(attr, self.name, self.gets, self.sets)
    #     else:
    #         caller = inspect.currentframe().f_back
    #         object.__getattribute__(self, "gets").append(
    #             [self.name, caller.f_code.co_filename.split("\\")[-1], str(caller.f_lineno)])
    #         return attr
    #
    # def __setitem__(self, key, value):
    #     # print(self.name,value)
    #     caller = inspect.currentframe().f_back
    #     self.sets.append(
    #         [self.name, type(value).__name__, caller.f_code.co_filename.split("\\")[-1], caller.f_lineno])
    #     np.ndarray.__setitem__(self, key, value)


@memoize
def Infiltration(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                 ISRR, ISRA, CN):
    result = np.zeros((NYrs, 12, 31))
    qtotal = QTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if qtotal[Y][i][j] <= water[Y][i][j]:
                    result[Y][i][j] = water[Y][i][j] - qtotal[Y][i][j]
    return result


def Infiltration_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                 ISRR, ISRA, CN):
    result = np.zeros((NYrs, 12, 31))
    qtotal = QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result[np.where(qtotal < water)] = water[np.where(qtotal < water)] - qtotal[np.where(qtotal < water)]
    return result

try:
    from gwlfe_compiled import InitSnow_2_inner
except ImportError:
    print("Unable to import compiled InitSnow_inner, using slower version")
    from InitSnow_inner import InitSnow_2_inner


# @memoize
def InitSnow(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    result = np.zeros((NYrs, 12, 31))
    yesterday = InitSnow_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0:
                    result[Y][i][j] = yesterday + Prec[Y][i][j]
                else:
                    if yesterday > 0.001:
                        result[Y][i][j] = max(yesterday - 0.45 * Temp[Y][i][j], 0)
                    else:
                        result[Y][i][j] = yesterday
                yesterday = result[Y][i][j]
    return result


@memoize
def InitSnow_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    return InitSnow_2_inner(NYrs, DaysMonth, InitSnow_0, Temp, Prec)

try:
    from gwlfe_compiled import InitSnowYesterday_inner
except ImportError:
    print("Unable to import compiled InitSnowYesterday_inner, using slower version")
    from InitSnowYesterday_inner import InitSnowYesterday_inner


def InitSnowYesterday(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    return InitSnowYesterday_inner(NYrs, DaysMonth, InitSnow_0, Temp, Prec)



# @memoize
def LE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
       ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
       , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal
       , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust):
    result = np.zeros((NYrs, 12))
    sedafactor = SedAFactor(NumAnimals, AvgAnimalWt, NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area, SedAFactor_0, AvKF,
                            AvSlope, SedAAdjust)
    streamflowvol = StreamFlowVol(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper,
                                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef
                                  , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                  StreamWithdrawal, GroundWithdrawal)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = sedafactor * (StreamFlowVolAdj * (streamflowvol[Y][i] ** 0.6))
    return result

def LE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
         ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
         , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal
         , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust):
    sedafactor = SedAFactor(NumAnimals, AvgAnimalWt, NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area, SedAFactor_0, AvKF,
                            AvSlope, SedAAdjust)#TODO: this has apparently been vectorized but is on a different branch
    streamflowvol = StreamFlowVol_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper,
                                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef
                                  , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                  StreamWithdrawal, GroundWithdrawal)
    return sedafactor * StreamFlowVolAdj * streamflowvol ** 0.6



@memoize
def Load(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                        SweepFrac, UrbSweepFrac, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 3))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    netdisload = NetDisLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                        SweepFrac, UrbSweepFrac, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    netsolidload = NetSolidLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                        SweepFrac, UrbSweepFrac, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for q in range(Nqual):
                        result[Y][i][q] += netdisload[Y][i][j][q] + netsolidload[Y][i][j][q]
                        if result[Y][i][q] < 0:
                            result[Y][i][q] = 0
                else:
                    pass
    return result


def Load_2():
    pass

# -*- coding: utf-8 -*-

"""
Imported from LoadReductions.bas
"""


log = logging.getLogger(__name__)


def AdjustScnLoads(z):
    # Check for zero values
    if z.n23 == 0:
        z.n23 = 0.0000001
    if z.n24 == 0:
        z.n24 = 0.0000001
    if z.n42 == 0:
        z.n42 = 0.0000001

    # Estimate sediment reductions for row crops based on ag BMPs
    SROWBMP1 = (z.n25 / 100) * z.n1 * z.n79
    SROWBMP2 = (z.n26 / 100) * z.n1 * z.n81
    SROWBMP3 = (z.n27 / 100) * z.n1 * z.n82
    SROWBMP4 = (z.n27b / 100) * z.n1 * z.n82b
    SROWBMP5 = (z.n28 / 100) * z.n1 * z.n83
    SROWBMP8 = (z.n29 / 100) * z.n1 * z.n84
    SROWRED = z.n1 - (SROWBMP1 + SROWBMP2 + SROWBMP3 + SROWBMP4 + SROWBMP5 + SROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if z.n42 > 0:
            SROWSM1 = (z.n43 / z.n42) * SROWRED * z.n80
        if z.n42 > 0:
            SROWSM2 = (z.n46c / z.n42) * SROWRED * z.n85d
        SROWBUF = SROWSM1 + SROWSM2
    else:
        if (z.n42 > 0):
            SROWBUF = (z.n43 / z.n42) * SROWRED * z.n80

    n1Start = z.n1
    z.n1 = SROWRED - SROWBUF
    if (z.n1 < (n1Start * 0.05)):
        z.n1 = n1Start * 0.05

    # Calculate total nitrogen reduction for row crops based on ag BMPs
    NROWBMP6 = (z.n28b / 100) * z.n5 * z.n70
    NROWNM = z.n5 - NROWBMP6
    NROWBMP1 = (z.n25 / 100) * NROWNM * z.n63
    NROWBMP2 = (z.n26 / 100) * NROWNM * z.n65
    NROWBMP3 = (z.n27 / 100) * NROWNM * z.n66
    NROWBMP4 = (z.n27b / 100) * NROWNM * z.n66b
    NROWBMP5 = (z.n28 / 100) * NROWNM * z.n67
    NROWBMP8 = (z.n29 / 100) * NROWNM * z.n68
    NROWRED = NROWNM - (NROWBMP1 + NROWBMP2 + NROWBMP3 + NROWBMP4 + NROWBMP5 + NROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            NROWSM1 = (z.n43 / z.n42) * NROWRED * z.n64
        if (z.n42 > 0):
            NROWSM2 = (z.n46c / z.n42) * NROWRED * z.n69c
        NROWBUF = NROWSM1 + NROWSM2
    else:
        if (z.n42 > 0):
            NROWBUF = (z.n43 / z.n42) * NROWRED * z.n64

    n5Start = z.n5
    z.n5 = NROWRED - NROWBUF
    if (z.n5 < (n5Start * 0.05)):
        z.n5 = n5Start * 0.05

    # Calculate dissolved nitrogen reduction for row crops based on ag BMPs
    NROWBMP6 = (z.n28b / 100) * z.n5dn * z.n70
    NROWNM = z.n5dn - NROWBMP6
    NROWBMP1 = (z.n25 / 100) * NROWNM * z.n63
    NROWBMP2 = (z.n26 / 100) * NROWNM * z.n65
    NROWBMP3 = (z.n27 / 100) * NROWNM * z.n66
    NROWBMP4 = (z.n27b / 100) * NROWNM * z.n66b
    NROWBMP5 = (z.n28 / 100) * NROWNM * z.n67
    NROWBMP8 = (z.n29 / 100) * NROWNM * z.n68
    NROWRED = NROWNM - (NROWBMP1 + NROWBMP2 + NROWBMP3 + NROWBMP4 + NROWBMP5 + NROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            NROWSM1 = (z.n43 / z.n42) * NROWRED * z.n64
        if (z.n42 > 0):
            NROWSM2 = (z.n46c / z.n42) * NROWRED * z.n69c
        NROWBUF = NROWSM1 + NROWSM2
    else:
        if (z.n42 > 0):
            NROWBUF = (z.n43 / z.n42) * NROWRED * z.n64

    n5dnStart = z.n5dn
    z.n5dn = NROWRED - NROWBUF
    if (z.n5dn < (n5dnStart * 0.05)):
        z.n5dn = n5dnStart * 0.05

    # Calculate total phosphorus reduction for row crops based on ag BMPs
    PROWBMP6 = (z.n28b / 100) * z.n12 * z.n78
    PROWNM = z.n12 - PROWBMP6
    PROWBMP1 = (z.n25 / 100) * PROWNM * z.n71
    PROWBMP2 = (z.n26 / 100) * PROWNM * z.n73
    PROWBMP3 = (z.n27 / 100) * PROWNM * z.n74
    PROWBMP4 = (z.n27b / 100) * PROWNM * z.n74b
    PROWBMP5 = (z.n28 / 100) * PROWNM * z.n75

    PROWBMP8 = (z.n29 / 100) * PROWNM * z.n76
    PROWRED = PROWNM - (PROWBMP1 + PROWBMP2 + PROWBMP3 + PROWBMP4 + PROWBMP5 + PROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            PROWSM1 = (z.n43 / z.n42) * PROWRED * z.n72
        if (z.n42 > 0):
            PROWSM2 = (z.n46c / z.n42) * PROWRED * z.n77c
        PROWBUF = PROWSM1 + PROWSM2
    else:
        if (z.n42 > 0):
            PROWBUF = (z.n43 / z.n42) * PROWRED * z.n72

    z.n12Start = z.n12
    z.n12 = PROWRED - PROWBUF
    if (z.n12 < (z.n12Start * 0.05)):
        z.n12 = z.n12Start * 0.05

    # Calculate dissolved phosphorus reduction for row crops based on ag BMPs
    PROWBMP6 = (z.n28b / 100) * z.n12dp * z.n78
    PROWNM = z.n12dp - PROWBMP6
    PROWBMP1 = (z.n25 / 100) * PROWNM * z.n71
    PROWBMP2 = (z.n26 / 100) * PROWNM * z.n73
    PROWBMP3 = (z.n27 / 100) * PROWNM * z.n74
    PROWBMP4 = (z.n27b / 100) * PROWNM * z.n74b
    PROWBMP5 = (z.n28 / 100) * PROWNM * z.n75

    PROWBMP8 = (z.n29 / 100) * PROWNM * z.n76
    PROWRED = PROWNM - (PROWBMP1 + PROWBMP2 + PROWBMP3 + PROWBMP4 + PROWBMP5 + PROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            PROWSM1 = (z.n43 / z.n42) * PROWRED * z.n72
        if (z.n42 > 0):
            PROWSM2 = (z.n46c / z.n42) * PROWRED * z.n77c
        PROWBUF = PROWSM1 + PROWSM2
    else:
        if (z.n42 > 0):
            PROWBUF = (z.n43 / z.n42) * PROWRED * z.n72

    n12dpStart = z.n12dp
    z.n12dp = PROWRED - PROWBUF
    if (z.n12dp < (n12dpStart * 0.05)):
        z.n12dp = n12dpStart * 0.05

    # Calculate sed reduction for hay/pasture based on ag BMPs
    SHAYBMP4 = (z.n33c / 100) * z.n2 * z.n82b
    SHAYBMP5 = (z.n35 / 100) * z.n2 * z.n83
    SHAYBMP7 = (z.n36 / 100) * z.n2 * z.n84b
    SHAYBMP8 = (z.n37 / 100) * z.n2 * z.n84

    n2Start = z.n2
    z.n2 = z.n2 - (SHAYBMP4 + SHAYBMP5 + SHAYBMP7 + SHAYBMP8)
    if (z.n2 < (n2Start * 0.05)):
        z.n2 = n2Start * 0.05

    # Calculate total nitrogen reduction for hay/pasture based on different percent usage of BMPs
    NHAYBMP6 = (z.n35b / 100) * z.n6 * z.n70
    NHAYNM = z.n6 - NHAYBMP6
    NHAYBMP4 = (z.n33c / 100) * NHAYNM * z.n66b
    NHAYBMP5 = (z.n35 / 100) * NHAYNM * z.n67
    NHAYBMP7 = (z.n36 / 100) * NHAYNM * z.n68b
    NHAYBMP8 = (z.n37 / 100) * NHAYNM * z.n68

    n6Start = z.n6
    z.n6 = NHAYNM - (NHAYBMP4 + NHAYBMP5 + NHAYBMP7 + NHAYBMP8)
    if (z.n6 < (n6Start * 0.05)):
        z.n6 = n6Start * 0.05

    # Calculate dissolved nitrogen reduction for hay/pasture
    NHAYBMP6 = (z.n35b / 100) * z.n6dn * z.n70
    NHAYNM = z.n6dn - NHAYBMP6
    NHAYBMP4 = (z.n33c / 100) * NHAYNM * z.n66b
    NHAYBMP5 = (z.n35 / 100) * NHAYNM * z.n67
    NHAYBMP7 = (z.n36 / 100) * NHAYNM * z.n68b
    NHAYBMP8 = (z.n37 / 100) * NHAYNM * z.n68

    n6dnStart = z.n6dn
    z.n6dn = NHAYNM - (NHAYBMP4 + NHAYBMP5 + NHAYBMP7 + NHAYBMP8)
    if (z.n6dn < (n6dnStart * 0.05)):
        z.n6dn = n6dnStart * 0.05

    # Calculate total phosphorus reduction for hay/pasture based on different percent usage of BMPs
    PHAYBMP6 = (z.n35b / 100) * z.n13 * z.n78
    PHAYNM = z.n13 - PHAYBMP6
    PHAYBMP4 = (z.n33c / 100) * PHAYNM * z.n74b
    PHAYBMP5 = (z.n35 / 100) * PHAYNM * z.n75
    PHAYBMP7 = (z.n36 / 100) * PHAYNM * z.n76b
    PHAYBMP8 = (z.n37 / 100) * PHAYNM * z.n76

    n13Start = z.n13
    z.n13 = PHAYNM - (PHAYBMP4 + PHAYBMP5 + PHAYBMP7 + PHAYBMP8)
    if (z.n13 < (n13Start * 0.05)):
        z.n13 = n13Start * 0.05

    # Calculate dissolved phosphorus reduction for hay/pasture
    PHAYBMP6 = (z.n35b / 100) * z.n13dp * z.n78
    PHAYNM = z.n13dp - PHAYBMP6
    PHAYBMP4 = (z.n33c / 100) * PHAYNM * z.n74b
    PHAYBMP5 = (z.n35 / 100) * PHAYNM * z.n75
    PHAYBMP7 = (z.n36 / 100) * PHAYNM * z.n76b
    PHAYBMP8 = (z.n37 / 100) * PHAYNM * z.n76

    n13dpStart = z.n13dp
    z.n13dp = PHAYNM - (PHAYBMP4 + PHAYBMP5 + PHAYBMP7 + PHAYBMP8)
    if (z.n13dp < (n13dpStart * 0.05)):
        z.n13dp = n13dpStart * 0.05

    # Calculate nitrogen reducton for animal activities based on differnt percent usage of BMPs
    # NAWMSL = (z.n41b / 100) * z.n85h * z.GRLBN
    # NAWMSP = (z.n41d / 100) * z.n85j * z.NGLBN
    # NRUNCON = (z.n41f / 100) * z.n85l * (z.GRLBN + z.NGLBN)
    # if z.n42 > 0:
    # NFENCING = (z.n45 / z.n42) * z.n69 * z.GRSN
    # NAGBUFFER = (z.n43 / z.n42) * z.n64 * (z.AvAnimalNSum - (z.NGLBN + z.GRLBN + z.GRSN))

    # z.n7b = z.AvAnimalNSum - (z.NAWMSL + z.NAWMSP + z.NRUNCON + z.NFENCING + z.NAGBUFFER)

    # Calculate phosphorus reduction for animal activities based on different percent of BMPs
    PAWMSL = (z.n41b / 100) * z.n85i * z.GRLBP
    PAWMSP = (z.n41d / 100) * z.n85k * z.NGLBP
    PRUNCON = (z.n41f / 100) * z.n85m * (z.GRLBP + z.NGLBP)
    PHYTASEP = (z.n41h / 100) * z.n85n * (z.NGLManP + z.NGLBP)
    if z.n42 > 0:
        PFENCING = (z.n45 / z.n42) * z.n77 * z.GRSP
        PAGBUFFER = (z.n43 / z.n42) * z.n72 * (z.n14b - (z.NGLBP + z.GRLBP + z.GRSP))

    z.n14b = z.n14b - (PAWMSL + PAWMSP + PRUNCON + PHYTASEP + PFENCING + PAGBUFFER)

    # Calculate Urban Load Reductions

    # High Urban S load
    # Urban Sediment Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    SURBWETH = z.n25b * z.n2b * z.n85b
    z.n2b = z.n2b - SURBWETH
    if z.n2b < 0:
        z.n2b = 0

    # . . . Low-density areas
    SURBWETL = z.n25b * z.n2c * z.n85b
    z.n2c = z.n2c - SURBWETL
    if z.n2c < 0:
        z.n2c = 0

    # Urban Nitrogen Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    NURBWETH = z.n25b * z.n6b * z.n69b
    z.n6b = z.n6b - NURBWETH
    if z.n6b < 0:
        z.n6b = 0

    # Urban Dissolved Nitrogen Reduction
    NURBWETH = z.n25b * z.n6bdn * z.n69b
    z.n6bdn = z.n6bdn - NURBWETH
    if z.n6bdn < 0:
        z.n6bdn = 0

    # . . . Low-density areas
    NURBWETL = z.n25b * z.n6c * z.n69b
    z.n6c = z.n6c - NURBWETL
    if z.n6c < 0:
        z.n6c = 0

    # Urban Dissolved Nitrogen Reduction
    NURBWETL = z.n25b * z.n6cdn * z.n69b
    z.n6cdn = z.n6cdn - NURBWETL
    if z.n6cdn < 0:
        z.n6cdn = 0

    # Urban Phosphorus Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    PURBWETH = z.n25b * z.n13b * z.n77b
    z.n13b = z.n13b - PURBWETH
    if z.n13b < 0:
        z.n13b = 0

    # Urban Dissolved Phosphorus Reduction
    PURBWETH = z.n25b * z.n13bdp * z.n77b
    z.n13bdp = z.n13bdp - PURBWETH
    if z.n13bdp < 0:
        z.n13bdp = 0

    # . . . Low-density areas
    PURBWETL = z.n25b * z.n13c * z.n77b
    z.n13c = z.n13c - PURBWETL
    if z.n13c < 0:
        z.n13c = 0

    # Urban Dissolved Phosphorus Reduction
    PURBWETL = z.n25b * z.n13cdp * z.n77b
    z.n13cdp = z.n13cdp - PURBWETL
    if z.n13cdp < 0:
        z.n13cdp = 0

    # Farm animal FC load reductions
    FCAWMSL = (z.n41b / 100) * z.n85q * z.GRLBFC
    FCAWMSP = (z.n41d / 100) * z.n85r * z.NGLBFC
    FCRUNCON = (z.n41f / 100) * z.n85s * (z.NGLBFC + z.GRLBFC)
    FCFENCING = (z.n45 / z.n42) * z.n85p * z.GRSFC
    FCAGBUFFER = (z.n43 / z.n42) * z.n85o * (z.n139 - (z.NGLBFC + z.GRLBFC + z.GRSFC))
    if FCAGBUFFER < 0:
        FCAGBUFFER = 0

    # For Animal FC
    z.n145 = z.n139 - (FCAWMSL + FCAWMSP + FCRUNCON + FCFENCING + FCAGBUFFER)
    if z.n145 < 0:
        z.n145 = 0

    # For urban FC
    FCURBBIO = z.n142 * z.RetentEff * z.n85u
    FCURBWET = z.n142 * z.n25b * z.n85t
    FCURBBUF = z.n142 * FilterEff(z.FilterWidth) * z.PctStrmBuf * z.n85o
    z.n148 = z.n142 - (FCURBBIO + FCURBWET + FCURBBUF)
    if z.n148 < 0:
        z.n148 = 0

    # Calculations for Unpaved Roads N, P and Sed Load Reduction
    if z.n42c > 0:
        SEDUNPAVED = (z.n46o / z.n42c) * z.n2d * z.n85g * 1.4882
        z.n2d = z.n2d - SEDUNPAVED
        if z.n2d < 0:
            z.n2d = 0

        NUNPAVED = (z.n46o / z.n42c) * z.n6d * z.n85e * 1.4882
        z.n6d = z.n6d - NUNPAVED
        if z.n6d < 0:
            z.n6d = 0

        NUNPAVED = (z.n46o / z.n42c) * z.n6ddn * z.n85e * 1.4882
        z.n6ddn = z.n6ddn - NUNPAVED
        if z.n6ddn < 0:
            z.n6ddn = 0

        PUNPAVED = (z.n46o / z.n42c) * z.n13d * z.n85f * 1.4882
        z.n13d = z.n13d - PUNPAVED
        if z.n13d < 0:
            z.n13d = 0

        PUNPAVED = (z.n46o / z.n42c) * z.n13ddp * z.n85f * 1.4882
        z.n13ddp = z.n13ddp - PUNPAVED
        if z.n13d < 0:
            z.n13ddp = 0



@memoize
def LU(NRur, NUrb):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((nlu,)).astype("int")
    for l in range(NRur, nlu):
        result[l] = l - NRur
    return result

# @time_function
#lu is faster than lu_2
# def lu_2(NRur, NUrb):
#     nlu = NLU(NRur, NUrb)
#     result = np.zeros((nlu,)).astype("int")
#     result[NRur:nlu] = np.asarray(range(NRur, nlu)) - NRur
#     return result



@memoize
def LuDisLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
              Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
              LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 16, 3))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    dissurfaceload = DisSurfLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                 Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv,
                                 Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][l][q] += dissurfaceload[Y][i][j][l][q]
                    else:
                        pass
                else:
                    pass
    return result


@memoize
def LuDisLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv,
                Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    return np.sum(DisSurfLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv,
                                Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf), axis=(1, 2))


def LuErosion(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Acoef, KF, LS,
              C, P, Area):
    result = np.zeros((NYrs, 16))
    eros_washoff = ErosWashoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Acoef, KF, LS,
                               C, P, Area)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(NRur):
                result[Y][l] += eros_washoff[Y][l][i]
    return result

@memoize
def LuErosion_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, Acoef, KF, LS,
                C, P, Area):
    return np.sum(ErosWashoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, Acoef, KF, LS,
                                C, P, Area), axis=2)



@memoize
def LuLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
           Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
           LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 16, 3))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    surfaceload_1 = SurfaceLoad_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0,
                                  Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm,
                                  UrbBMPRed, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][l][q] += surfaceload_1[Y][i][j][l][q]
                    else:
                        pass
                else:
                    pass
    return result

@memoize
def LuLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
             Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
             LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf):
    return np.sum(SurfaceLoad_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv,
                                  Storm, UrbBMPRed, FilterWidth, PctStrmBuf), axis=(1, 2))



def LuRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0,
             AntMoist_0, Grow_0, Imper, ISRR, ISRA, CN):
    result = np.zeros((NYrs, 16))
    nlu = NLU_function(NRur, NUrb)
    urb_q_runoff = UrbQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0,
                              AntMoist_0, Grow_0, Imper, ISRR, ISRA)
    rur_q_runoff = RurQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            # Calculate landuse runoff for rural areas
            for l in range(NRur):
                result[Y][l] += rur_q_runoff[Y][l][i]
        for i in range(12):
            # Calculate landuse runoff for urban areas
            for l in range(NRur, nlu):
                result[Y][l] += urb_q_runoff[Y][l][i]
    return result

@memoize
def LuRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0,
               AntMoist_0, Grow_0, Imper, ISRR, ISRA, CN):
    return np.hstack(
        (np.sum(RurQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0), axis=1),
         np.sum(UrbQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0,
                             AntMoist_0, Grow_0, Imper, ISRR, ISRA), axis=1),
         ))



def LuTotNitr(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
              Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
              FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, CNP_0, Imper, ISRR, ISRA,
              Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf, Acoef,
              CNI_0, Nqual):
    result = np.zeros((NYrs, 16))
    n_runoff = nRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                       Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                       FirstManureMonth2, LastManureMonth2)
    sed_deliv_ratio = SedDelivRatio(SedDelivRatio_0)
    eros_washoff = ErosWashoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Acoef,
                               KF, LS,
                               C, P, Area)
    lu_load = LuLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                     AntMoist_0,
                     Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual,
                     LoadRateImp,
                     LoadRatePerv, Storm, UrbBMPRed,
                     FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            # Add in the urban calucation for sediment
            for l in range(NRur):
                result[Y][l] += n_runoff[Y][i]
                result[Y][l] += 0.001 * sed_deliv_ratio * eros_washoff[Y][l][i] * SedNitr
                result[Y][l] += lu_load[Y][l][0] / NYrs / 2
    return result


@memoize
def LuTotNitr_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, Acoef):
    n_runoff = np.reshape(
        np.repeat(np.sum(nRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                                   Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                                   FirstManureMonth2, LastManureMonth2), axis=1), repeats=10), (NYrs, 10))
    sed_deliv_ratio = SedDelivRatio(SedDelivRatio_0)
    eros_washoff = np.sum(ErosWashoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, Acoef,
                                        KF, LS,
                                        C, P, Area), axis=1)
    # lu_load = LuLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
    #                  AntMoist_0,
    #                  Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual,
    #                  LoadRateImp,
    #                  LoadRatePerv, Storm, UrbBMPRed,
    #                  FilterWidth, PctStrmBuf)[:,:,0]
    # luLoad is not needed because it is only defined for NUrb land use, and the others are only defined for NRur
    return n_runoff + 0.001 * sed_deliv_ratio * eros_washoff * SedNitr  # + lu_load / NYrs / 2



def LuTotNitr_1(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, CN, Grow_0,
                Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, CNP_0, Imper, ISRR, ISRA,
                Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf, Acoef,
                CNI_0, Nqual, ShedAreaDrainLake, RetentNLake, AttenFlowDist, AttenFlowVel, AttenLossRateN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, nlu))
    lu_tot_nitr = LuTotNitr(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                            Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                            FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, CNP_0, Imper,
                            ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
                            FilterWidth, PctStrmBuf, Acoef, CNI_0, Nqual)
    retent_factor_n = RetentFactorN(ShedAreaDrainLake, RetentNLake)
    atten_n = AttenN(AttenFlowDist, AttenFlowVel, AttenLossRateN)
    for y in range(NYrs):
        for l in range(nlu):
            result[y][l] = round((lu_tot_nitr[y][l] * retent_factor_n * (1 - atten_n)))
    return result


@memoize
def LuTotNitr_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, NitrConc, ManNitr,
                  ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2, SedDelivRatio_0,
                  KF, LS, C, P, SedNitr, Acoef, ShedAreaDrainLake, RetentNLake, AttenFlowDist, AttenFlowVel,
                  AttenLossRateN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, nlu))
    lu_tot_nitr = LuTotNitr_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                              Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                              FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, Acoef)
    retent_factor_n = RetentFactorN(ShedAreaDrainLake, RetentNLake)
    atten_n = AttenN(AttenFlowDist, AttenFlowVel, AttenLossRateN)
    # TODO: this is only a temporary fix until WriteOutputfiles has been fully extracted
    result[:, :NRur] = np.round((lu_tot_nitr * retent_factor_n * (1 - atten_n)))
    return result



@memoize
def LuTotPhos(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc, ManPhos,
              ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF,
              LS, C, P, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm,
              UrbBMPRed, FilterWidth, PctStrmBuf, Acoef, SedPhos, CNI_0):
    result = np.zeros((NYrs, 16))
    p_runoff = pRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc,
                       ManuredAreas, FirstManureMonth, LastManureMonth, ManPhos, FirstManureMonth2,
                       LastManureMonth2)
    sed_deliv_ratio = SedDelivRatio(SedDelivRatio_0)
    eros_washoff = ErosWashoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Acoef,
                               KF, LS, C, P, Area)
    lu_load = LuLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                     AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual,
                     LoadRateImp, LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            # Add in the urban calucation for sediment
            for l in range(NRur):
                result[Y][l] += p_runoff[Y][i]
                result[Y][l] += 0.001 * sed_deliv_ratio * eros_washoff[Y][l][i] * SedPhos
                result[Y][l] += lu_load[Y][l][1] / NYrs / 2
    return result

def LuTotPhos_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc, ManPhos,
                ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2, SedDelivRatio_0,
                KF, LS, C, P, Acoef, SedPhos):
    p_runoff = np.reshape(
        np.repeat(np.sum(
            pRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc,
                      ManuredAreas,
                      FirstManureMonth, LastManureMonth, ManPhos, FirstManureMonth2, LastManureMonth2), axis=1),
            repeats=10), (NYrs, 10))
    sed_deliv_ratio = SedDelivRatio(SedDelivRatio_0)
    eros_washoff = np.sum(ErosWashoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, Acoef,
                                        KF, LS, C, P, Area), axis=1)
    # luLoad is not needed because it is only defined for NUrb land use, and the others are only defined for NRur
    return p_runoff + 0.001 * sed_deliv_ratio * eros_washoff * SedPhos  # + lu_load / NYrs / 2



@memoize
def LU_1(NRur, NUrb):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((nlu,)).astype("int")
    for l in range(NRur, nlu):
        result[l] = l - 11
    return result

#Tried, it was slower. LU_1 is faster
# def LU_1_2():
#     pass


# @memoize
def Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec):
    result = np.zeros((NYrs, 12, 31))
    init_snow = InitSnow(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    init_snow_yesterday = InitSnow_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and init_snow_yesterday > 0.001:
                    result[Y][i][j] = 0.45 * Temp[Y][i][j]
                else:
                    result[Y][i][j] = 0
                init_snow_yesterday = init_snow[Y][i][j]
    return result

def Melt_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec):
    init_snow_yesterday = InitSnowYesterday(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    return np.where((Temp>0) & (init_snow_yesterday > 0.001), 0.45 * Temp, 0)


# Not used in other calculations
@memoize
def MeltPest(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    result = np.zeros((NYrs, 12, 31))
    init_snow = InitSnow(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    init_snow_yesterday = InitSnow_0
    melt = Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and init_snow_yesterday > 0.001:
                    if melt[Y][i][j] > init_snow_yesterday:
                        # TODO: code seems to run fine with with only these three condidtions anded together
                        result[Y][i][j] = init_snow_yesterday
                    else:
                        result[Y][i][j] = melt[Y][i][j]
                else:
                    result[Y][i][j] = 0
                init_snow_yesterday = init_snow[Y][i][j]
    return result


def MeltPest_2():
    pass


@memoize
def Melt_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    result = np.zeros((NYrs, 12, 31))
    init_snow = InitSnow(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    init_snow_yesterday = InitSnow_0
    melt = Melt(NYrs, DaysMonth, Temp, InitSnow_0, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and init_snow_yesterday > 0.001 and melt[Y][i][j] > init_snow_yesterday:
                    result[Y][i][j] = init_snow_yesterday
                else:
                    result[Y][i][j] = melt[Y][i][j]
                init_snow_yesterday = init_snow[Y][i][j]
    return result

@memoize
def Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    # result = np.zeros((NYrs, 12, 31))
    init_snow_yesterday = InitSnowYesterday(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    melt = Melt_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec)
    melt[np.where((Temp> 0) & (init_snow_yesterday > 0.001) & (melt > init_snow_yesterday))] = init_snow_yesterday[np.where((Temp> 0) & (init_snow_yesterday > 0.001) & (melt > init_snow_yesterday))]
    return melt

# without
# 300 loops of 'test_test', average time per loop: 0.321625, best: 0.303278, worst: 0.426772
# 300 loops of 'test_test', average time per loop: 0.006865, best: 0.001217, worst: 0.016353
# def memoize_with_args(f):
#     return f

def memoize_with_args(f):
    class memodict():
        def __init__(self, f):
            self.f = f
            self.result = {}
            self.__name__ = f.__name__

        def __call__(self, *args):
            args_string = f.__name__
            for arg in args:
                if (isinstance(arg, np.ndarray)):
                    args_string += hashlib.sha1(arg).hexdigest() + ","
                else:
                    args_string += hashlib.sha1(str(arg)).hexdigest() + ","
            try:
                return self.result[args_string]
            except KeyError:
                self.result[args_string] = self.f(*args)
                return self.result[args_string]

    return memodict(f)


# 300 loops of 'test_test', average time per loop: 0.000156, best: 0.000117, worst: 0.000521
# def memoize(f):
#     class memodict():
#         def __init__(self, f):
#             self.f = f
#             self.result = None
#         def __call__(self,*args):
#             # if self.result is None:
#             #     ret = self.result = self.f(*args)
#             #     return ret
#             return self.f(*args)
#     return memodict(f)


def memodict(f):
    class memodict(dict):
        def __missing__(self, *args):
            ret = self['result'] = f(*args)
            return ret

        def __getitem__(self, *args):
            return dict.__getitem__(self, 'result')

    return memodict().__getitem__


# def memoize(f):
#     return f
# runid = uuid.uuid4()
# runids = {}
def memoize(f):
    class memodict(dict):
        def __init__(self, f):
            self.f = f
            self.result = None
            self.__name__ = f.__name__
        def __call__(self, *args):
            # print(runid == self.runid)
            if (self.result is None):
                self.result = self.f(*args)
                # ret = self.result = self.f(*args)
            return self.result

    return memodict(f)

def memoize_runid(f):
    class memodict(dict):
        def __init__(self, f):
            self.f = f
            self.result = None
            self.__name__ = f.__name__
            self.runid = None

        def __call__(self, *args):
            # print(runid == self.runid)
            if (self.result is None) or (self.runid != runid):
                self.runid = uuid.UUID(runid.hex)
                self.result = self.f(*args)
                # ret = self.result = self.f(*args)
            return self.result

    return memodict(f)
# def memoize(f):
#     class memodict():
#         def __init__(self, f):
#             self.f = f
#             self.result = None
#             self.__name__ = f.__name__
#
#         def __call__(self, *args):
#             return self.f(*args)
#
#     return memodict(f)

# def memoize_list(f):
#     """ Memoization decorator for functions taking one or more arguments. """
#     class memodict(dict):
#         def __init__(self, f):
#             self.f = f
#         def __call__(self):
#             return self[args]
#         def __missing__(self, key):
#             ret = self[key] = self.f(*key)
#             return ret
#     return memodict(f)



@time_function
def test_function1():
    test = np.ones((1000, 1000))
    return memoizied_function(test, test, test, test, test, test, test, test, test, test, test, test, test, test, test,
                              test, test, test, test, test, )


@memoize_with_args
def memoizied_function(*arg):
    sleep(0.3)
    return np.random.random((1000, 1000))

@time_function
def test_function2():
    test = np.ones((1000, 1000))
    return memoizied_function2(test, test, test, test, test, test, test, test, test, test, test, test, test, test, test,
                              test, test, test, test, test, )


@memoize
def memoizied_function2(*arg):
    sleep(0.3)
    return np.random.random((1000, 1000))

@time_function
def test_function3():
    test = np.ones((1000, 1000))
    return memoizied_function3(test, test, test, test, test, test, test, test, test, test, test, test, test, test, test,
                              test, test, test, test, test, )


@memoize
def memoizied_function3(*arg):
    sleep(0.3)
    return np.random.random((1000, 1000))


if __name__ == "__main__":
    test_function1()
    test_function2()
    test_function3()




def NConc(NRur, NUrb, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
          LastManureMonth2):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((12, nlu))
    for i in range(12):
        for l in range(NRur):
            result[i][l] = NitrConc[l]
            if l < ManuredAreas and i >= FirstManureMonth and i <= LastManureMonth:
                result[i][l] = ManNitr[l]
            if l < ManuredAreas and i >= FirstManureMonth2 and i <= LastManureMonth2:
                result[i][l] = ManNitr[l]
    return result


def NConc_2(NRur, NUrb, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
            LastManureMonth2):
    if (FirstManureMonth < 0 and FirstManureMonth2 < 0 and LastManureMonth < 0 and LastManureMonth2 < 0):
        return np.reshape(np.repeat(NitrConc[None, :], repeats=12, axis=0), (12, -1))
    else:
        nlu = NLU_function(NRur, NUrb)
        result = np.reshape(np.repeat(NitrConc, repeats=12, axis=0), (12, nlu))
        result[FirstManureMonth:LastManureMonth, :ManuredAreas] = ManNitr
        result[FirstManureMonth2:LastManureMonth2, :ManuredAreas] = ManNitr
        return result



@memoize
def NetDisLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
               Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
               LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 31, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    dissurfaceload = DisSurfLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                 Grow_0, CNP_0,
                                 Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp,
                                 LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][i][j][q] += dissurfaceload[Y][i][j][l][q]
                    else:
                        pass
                else:
                    pass
    return result


def NetDisLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                 Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                 LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    # nlu = NLU(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                          Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    dissurfaceload = DisSurfLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                   Grow_0, CNP_0,
                                   Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp,
                                   LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    nonzero = np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001))
    result[nonzero] = np.sum(dissurfaceload[nonzero], axis=1)
    return result



@memoize
def NetSolidLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                 Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                 LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 31, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    dissurfaceload = DisSurfLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                 Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    surfaceload_1 = SurfaceLoad_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,  LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][i][j][q] += surfaceload_1[Y][i][j][l][q] - dissurfaceload[Y][i][j][l][q]
                    else:
                        pass
                else:
                    pass
    return result


def NetSolidLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                   Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                   LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu-NRur,Nqual))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                          Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    dissurfaceload = DisSurfLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Nqual, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                   Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp,
                                   LoadRatePerv, Storm, UrbBMPRed, DisFract, FilterWidth, PctStrmBuf)
    surfaceload_1 = SurfaceLoad_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                    Grow_0,
                                    CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                                    LoadRatePerv,
                                    Storm, UrbBMPRed, FilterWidth, PctStrmBuf)
    nonzero = np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001))
    result[nonzero] = surfaceload_1[nonzero] - dissurfaceload[nonzero]
    return np.sum(result,axis=3)



@memoize
def NewCN(NRur, NUrb, CN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    for l in range(NRur):
        result[0][l] = CN[l] / (2.334 - 0.01334 * CN[l])
        result[2][l] = CN[l] / (0.4036 + 0.0059 * CN[l])
        if result[2][l] > 100:
            result[2][l] = 100
    return result

# @time_function
# @jit(cache=True, nopython = True)
@memoize
def NewCN_2(NRur, NUrb, CN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((3, nlu))
    result[0,:] = CN / (2.334 - 0.01334 * CN)
    result[2,:] = CN / (0.4036 + 0.0059 * CN)
    result[2,:][np.where(result[2,:]>100)] = 100
    return result


def NFEN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
         CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
         UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
         RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
         TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
         NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
         AvSlope, SedAAdjust, StreamLength, AgLength,
         n42, SedNitr, BankNFrac, n45, n69):
    result = np.zeros((NYrs, 12))
    streambank_n = StreamBankN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                               CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                               UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                               TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                               NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                               AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)

    agstrm = AGSTRM(AgLength, StreamLength)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = 0
            if n42 > 0:
                result[Y][i] = (n45 / n42) * streambank_n[Y][i] * agstrm * n69
    return result


def NFEN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
           CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
           UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
           RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
           TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
           NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
           AvSlope, SedAAdjust, StreamLength, AgLength,
           n42, SedNitr, BankNFrac, n45, n69):
    if n42 > 0:
        agstrm = AGSTRM_2(AgLength, StreamLength)
        streambank_n = StreamBankN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                     CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                     UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                     RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                     TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                     NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                     AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)
        return (n45 / n42) * streambank_n * agstrm * n69
    else:
        return np.zeros((NYrs, 12))



@memoize
def NLU_function(NRur, NUrb):
    return NRur + NUrb


# def NLU_2():
#     pass



@memoize
def nRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, NitrConc,
            ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2):
    result = np.zeros((NYrs, 12))
    rur_q_runoff = RurQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0)
    n_conc = NConc(NRur, NUrb, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
                   LastManureMonth2)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(NRur):
                result[Y][i] += 0.1 * n_conc[i][l] * rur_q_runoff[Y][l][i] * Area[l]
    return result


@memoize
def nRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, NitrConc,
              ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2):
    n_conc = NConc_2(NRur, NUrb, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
                   LastManureMonth2)[:, :NRur]

    return 0.1 * np.sum(n_conc *
                        RurQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN,
                                     Grow_0) * Area[:NRur], axis=2)



def NSTAB(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
          UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
          TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
          NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
          AvSlope, SedAAdjust, StreamLength, n42b, n46c, SedNitr, BankNFrac, n69c):
    result = np.zeros((NYrs, 12))
    streabank_n = StreamBankN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                              CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                              UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                              TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                              NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                              AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)

    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = 0
            if n42b > 0:
                result[Y][i] = (n46c / n42b) * streabank_n[Y][i] * n69c
    return result


def NSTAB_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
            CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
            UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
            RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
            TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
            NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
            AvSlope, SedAAdjust, StreamLength, n42b, n46c, SedNitr, BankNFrac, n69c):
    if n42b > 0:
        return (n46c / n42b) * StreamBankN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                             CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                             UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                             RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                             TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                             NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                             AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac) * n69c
    else:
        return np.zeros((NYrs, 12))


def NURBBANK(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
             CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
             UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
             RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
             TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
             NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
             AvSlope, SedAAdjust, StreamLength, n42b, UrbBankStab, SedNitr, BankNFrac, n69c):
    result = np.zeros((NYrs, 12))
    streambank_n = StreamBankN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                               CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                               UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                               TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                               NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                               AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (UrbBankStab / n42b) * streambank_n[Y][i] * n69c
    return result

def NURBBANK_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
               CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
               UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
               TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
               NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
               AvSlope, SedAAdjust, StreamLength, n42b, UrbBankStab, SedNitr, BankNFrac, n69c):
    return (UrbBankStab / n42b) * StreamBankN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                                CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                                UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                                RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                                TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                                NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                                AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac) * n69c

# -*- coding: utf-8 -*-




log = logging.getLogger(__name__)

EOL = '<EOL>'


def iterate_csv_values(fp):
    """
    Yield values as a continuous stream for each line in a
    file-like object.
    """
    reader = csv.reader(fp)
    line_no = 1
    for line in reader:
        col_no = 1
        for value in line:
            yield value, line_no, col_no
            col_no += 1
        yield EOL, line_no, col_no
        line_no += 1


class GmsReader(object):
    def __init__(self, fp):
        self.fp = iterate_csv_values(fp)

    def read(self):
        z = DataModel()

        # AFOs loss rate coefficients
        z.NgAWMSCoeffN = 0.14
        z.NgAWMSCoeffP = 0.14
        z.GrAWMSCoeffN = 0.75
        z.GrAWMSCoeffP = 0.75
        z.RunConCoeffN = 0.15
        z.RunConCoeffP = 0.15
        z.PhytaseCoeff = 0.16

        # z.ImpervAccum = np.zeros(16)
        # z.PervAccum = np.zeros(16)
        # z.QrunI = np.zeros(16)
        # z.QrunP = np.zeros(16)
        # z.WashPerv = np.zeros(16)
        # z.NetDisLoad = np.zeros(3)

        z.AvGRStreamFC = 0
        # z.AvGRStreamN = 0
        z.AvGRStreamP = 0
        # z.AvTileDrain = np.zeros(12)
        # z.RurAreaTotal = 0
        # z.UrbAreaTotal = 0
        z.d = np.zeros(12)
        z.KVD = np.zeros(12)
        z.CV = np.zeros(12)
        z.AreaE = np.zeros(16)
        z.KLSCP = np.zeros(16)
        z.UrbanNitr = np.zeros(16)
        z.UrbanPhos = np.zeros(16)
        z.AvStreamFlow = np.zeros(12)
        z.AvPrecipitation = np.zeros(12)
        # z.AvEvapoTrans = np.zeros(12)
        # z.AvGroundWater = np.zeros(12)
        # z.AvRunoff = np.zeros(12)
        # z.AvErosion = np.zeros(12)
        # z.AvSedYield = np.zeros(12)
        z.AFON = np.zeros(12)
        z.AFOP = np.zeros(12)
        z.AvLoad = np.zeros((12, 3))
        z.AvLuLoad = np.zeros((16, 3))
        z.AvDisLoad = np.zeros((16, 3))
        z.AvLuDisLoad = np.zeros((16, 3))
        # z.UrbSedLoad = np.zeros((16, 12))
        z.AvGroundNitr = np.zeros(12)
        z.AvGroundPhos = np.zeros(12)
        z.AvDisNitr = np.zeros(12)
        z.AvTotNitr = np.zeros(12)
        z.AvDisPhos = np.zeros(12)
        z.AvTotPhos = np.zeros(12)
        z.AvLuRunoff = np.zeros(16)
        z.AvLuErosion = np.zeros(16)
        z.AvLuSedYield = np.zeros(16)
        z.AvLuDisNitr = np.zeros(16)
        z.AvLuTotNitr = np.zeros(16)
        z.AvLuDisPhos = np.zeros(16)
        z.AvLuTotPhos = np.zeros(16)
        z.BSed = np.zeros(16)
        z.UrbanSed = np.zeros(16)
        z.UrbanErosion = np.zeros(16)
        # z.ErosWashoff = np.zeros((16, 12))
        z.QRunoff = np.zeros((16, 12))
        z.AgQRunoff = np.zeros((16, 12))
        # z.RurQRunoff = np.zeros((16, 12))
        # z.UrbQRunoff = np.zeros((16, 12))
        z.DailyLoad = np.zeros((50, 12, 31))
        z.SepticsDay = np.zeros(12)
        z.MonthlyLoad = np.zeros((12, 31))

        # Declare the daily values as ReDimensional arrays in
        # to Pesticide components
        z.DayPondNitr = np.zeros((12, 31))
        z.DayPondPhos = np.zeros((12, 31))
        z.DayNormNitr = np.zeros((12, 31))
        z.DayNormPhos = np.zeros((12, 31))
        # z.WashImperv = np.zeros(16)
        # z.NetSolidLoad = np.zeros(3)
        z.DayShortNitr = np.zeros((12, 31))
        z.DayShortPhos = np.zeros((12, 31))
        z.DayDischargeNitr = np.zeros((12, 31))
        z.DayDischargePhos = np.zeros((12, 31))
        z.PestAppMonth1 = np.zeros(16)
        z.PestAppYear1 = np.zeros(16)
        z.PestAppDate1 = np.zeros(16)
        z.PestAppMonth2 = np.zeros(16)
        z.PestAppYear2 = np.zeros(16)
        z.PestAppDate2 = np.zeros(16)
        z.PestShedName = np.zeros(12)
        z.PestCropArea = np.zeros(12)
        z.PestSoilBd = np.zeros(12)
        z.PestSoilAwc = np.zeros(12)
        z.PestSoilOm = np.zeros(12)
        z.PestCropName = np.zeros(12)
        z.PestName1 = np.zeros(16)
        z.PestRate1 = np.zeros(31)
        z.PestParamCarbon1 = np.zeros(16)
        z.PestParamWater1 = np.zeros(16)
        z.PestDecay1 = np.zeros(16)
        z.PestHalfLife1 = np.zeros(16)
        z.PestName2 = np.zeros(16)
        z.PestRate2 = np.zeros(31)
        z.PestParamCarbon2 = np.zeros(16)
        z.PestParamWater2 = np.zeros(16)
        z.PestDecay2 = np.zeros(16)
        z.PestHalfLife2 = np.zeros(16)
        # z.AvStreamBankEros = np.zeros(12)
        # z.AvStreamBankN = np.zeros(12)
        z.AvStreamBankP = np.zeros(12)
        z.CropPercent = np.zeros(12)
        z.PestSoilAwcCm = np.zeros(12)

        # Tile Drainage and Flow Variables
        # z.AvTileDrain = np.zeros(12)
        # z.AvWithdrawal = np.zeros(12)
        z.AvTileDrainN = np.zeros(12)
        z.AvTileDrainP = np.zeros(12)
        z.AvTileDrainSed = np.zeros(12)
        z.AvPtSrcFlow = np.zeros(12)

        # Calculated Values for Animal Feeding Operations
        # z.NGLoadN = np.zeros(9)
        z.NGLoadP = np.zeros(9)
        z.NGLoadFC = np.zeros(9)
        # z.NGAccManAppN = np.zeros(12)
        z.NGAccManAppP = np.zeros(12)
        z.NGAccManAppFC = np.zeros(12)
        # z.NGAppManN = np.zeros(12)
        # z.NGInitBarnN = np.zeros(12)
        z.NGAppManP = np.zeros(12)
        z.NGInitBarnP = np.zeros(12)
        z.NGAppManFC = np.zeros(12)
        z.NGInitBarnFC = np.zeros(12)

        # z.GRLoadN = np.zeros(9)
        z.GRLoadP = np.zeros(9)
        z.GRLoadFC = np.zeros(9)
        # z.GRAccManAppN = np.zeros(12)
        z.GRAccManAppP = np.zeros(12)
        z.GRAccManAppFC = np.zeros(12)
        # z.GRAppManN = np.zeros(12)
        # z.GRInitBarnN = np.zeros(12)
        z.GRAppManP = np.zeros(12)
        z.GRInitBarnP = np.zeros(12)
        z.GRAppManFC = np.zeros(12)
        z.GRInitBarnFC = np.zeros(12)
        # z.GrazingN = np.zeros(12)
        z.GrazingP = np.zeros(12)
        z.GrazingFC = np.zeros(12)
        z.GRStreamN = np.zeros(12)
        z.GRStreamP = np.zeros(12)
        z.GRStreamFC = np.zeros(12)
        # z.AvAnimalN = np.zeros(12)
        z.AvAnimalP = np.zeros(12)
        z.AvAnimalFC = np.zeros(12)
        z.AvWWOrgs = np.zeros(12)
        z.AvSSOrgs = np.zeros(12)
        z.AvUrbOrgs = np.zeros(12)
        z.AvWildOrgs = np.zeros(12)
        z.AvTotalOrgs = np.zeros(12)
        z.AvCMStream = np.zeros(12)
        z.AvOrgConc = np.zeros(12)
        # z.AvGRLostBarnN = np.zeros(12)
        z.AvGRLostBarnP = np.zeros(12)
        # z.AvNGLostBarnN = np.zeros(12)
        z.AvNGLostBarnP = np.zeros(12)
        z.AvNGLostManP = np.zeros(12)
        z.AvNGLostBarnFC = np.zeros(12)
        z.AvGRLostBarnFC = np.zeros(12)
        z.SweepFrac = np.zeros(12)

        z.q = 0
        z.k = 0
        # z.FilterEff = 0
        z.OutFiltWidth = 0
        z.Clean = 0
        z.CleanSwitch = 0
        z.OutletCoef = 0
        z.BasinVol = 0
        z.Volume = 0
        z.ActiveVol = 0
        z.DetentFlow = 0
        z.AnnDayHrs = 0
        # z.AreaTotal = 0
        z.FrozenPondNitr = 0
        z.FrozenPondPhos = 0
        z.AvSeptNitr = 0
        z.AvSeptPhos = 0
        # z.AgAreaTotal = 0
        z.ForestAreaTotal = 0

        # Referenced in LoadReductions
        # Mostly initialized in PublicVariables.bas
        z.SMCheck = 'Both'
        z.n5dn = 0
        z.n12dp = 0
        z.n13dp = 0
        z.n6dn = 0
        z.n6bdn = 0
        z.n6cdn = 0
        z.n13bdp = 0
        z.n13cdp = 0
        z.RetentEff = 0

        # Line 1:
        z.NRur = self.next(int)  # Number of Rural Land Use Categories
        z.NUrb = self.next(int)  # Number Urban Land Use Categories
        z.BasinId = self.next(int)  # Basin ID
        self.next(EOL)

        # z.NLU = z.NRur + z.NUrb

        # Line 2:
        z.TranVersionNo = self.next(str)  # GWLF-E Version
        z.RecessionCoef = self.next(float)  # Recession Coefficient
        z.SeepCoef = self.next(float)  # Seepage Coefficient
        # z.UnsatStor = self.next(float)  # Unsaturated Storage
        z.UnsatStor_0 = self.next(float)  # Unsaturated Storage
        # z.SatStor = self.next(float)  # Saturated Storage
        z.SatStor_0 = self.next(float)  # Saturated Storage
        # z.InitSnow = self.next(int)  # Initial Snow Days
        z.InitSnow_0 = self.next(int)  # Initial Snow Days
        # z.SedDelivRatio = self.next(float)  # Sediment Delivery Ratio
        z.SedDelivRatio_0 = self.next(float)  # Sediment Delivery Ratio
        z.MaxWaterCap = self.next(float)  # Average Available Water Capacity
        z.StreamLength = self.next(float)  # Total Stream Length (meters)
        z.AgLength = self.next(float)  # Agricultural Stream Length (meters)
        z.UrbLength = self.next(float)  # Urban Stream Length (meters)
        z.AgSlope3 = self.next(float)  # Area of agricultural land with slope > 3%
        z.AgSlope3to8 = self.next(float)  # Area of agricultural land with slope > 3% and < 8%
        z.AvSlope = self.next(float)  # Average % Slope
        z.AEU = self.next(float)  # Number of Animal Units
        z.WxYrs = self.next(int)  # Total Weather Years
        z.WxYrBeg = self.next(int)  # Beginning Weather Year
        z.WxYrEnd = self.next(int)  # Ending Weather Year
        # z.SedAFactor = self.next(float)  # Sediment A Factor
        z.SedAFactor_0 = self.next(float)  # Sediment A Factor
        z.TotArea = self.next(float)  # Total Basin Area (Ha)
        z.TileDrainRatio = self.next(float)  # Tile Drain Ratio
        z.TileDrainDensity = self.next(float)  # Tile Drain Density
        z.ETFlag = self.next(ETflag.parse)  # ET Flag
        z.AvKF = self.next(float)  # Average K Factor
        self.next(EOL)

        z.NYrs = z.WxYrs
        # TODO: Remove DimYrs
        z.DimYrs = z.WxYrs

        z.Load = np.zeros((z.DimYrs, 12, 3))
        z.DisLoad = np.zeros((z.DimYrs, 12, 3))
        # z.LuLoad = np.zeros((z.DimYrs, 16, 3))
        # z.LuDisLoad = np.zeros((z.DimYrs, 16, 3))
        z.UplandN = np.zeros((z.DimYrs, 12))
        z.UplandP = np.zeros((z.DimYrs, 12))
        z.UrbRunoffCm = np.zeros((z.DimYrs, 12))
        # z.UrbRunoffLiter = np.zeros((z.DimYrs, 12))
        # z.DailyFlow = np.zeros((z.DimYrs, 12, 31))
        z.DailyFlowMGD = np.zeros((z.DimYrs, 12, 31))
        # z.DailyFlowGPM = np.zeros((z.DimYrs, 12, 31))
        z.DailyPtSrcFlow = np.zeros((z.DimYrs, 12, 31))

        # Declare the daily values as ReDimensional arrays in
        # to Pesticide components
        z.DailyUplandSed = np.zeros((z.DimYrs, 12, 31))
        z.DailyUplandN = np.zeros((z.DimYrs, 12, 31))
        z.DailyUplandP = np.zeros((z.DimYrs, 12, 31))
        z.DailyTileDrainN = np.zeros((z.DimYrs, 12, 31))
        z.DailyTileDrainP = np.zeros((z.DimYrs, 12, 31))
        z.DailyStrmSed = np.zeros((z.DimYrs, 12, 31))
        z.DailySepticN = np.zeros((z.DimYrs, 12, 31))
        z.DailySepticP = np.zeros((z.DimYrs, 12, 31))
        z.DailyStrmN = np.zeros((z.DimYrs, 12, 31))
        z.DailyStrmP = np.zeros((z.DimYrs, 12, 31))
        z.DailyGroundN = np.zeros((z.DimYrs, 12, 31))
        z.DailyGroundP = np.zeros((z.DimYrs, 12, 31))
        z.DayGroundNitr = np.zeros((z.DimYrs, 12, 31))
        z.DayGroundPhos = np.zeros((z.DimYrs, 12, 31))
        z.DayDisPhos = np.zeros((z.DimYrs, 12, 31))
        z.DayDisNitr = np.zeros((z.DimYrs, 12, 31))
        z.DayTotNitr = np.zeros((z.DimYrs, 12, 31))
        z.DailyPointN = np.zeros((z.DimYrs, 12, 31))
        z.DailyPointP = np.zeros((z.DimYrs, 12, 31))
        z.DayTotPhos = np.zeros((z.DimYrs, 12, 31))
        z.DayLuTotN = np.zeros((16, z.DimYrs, 12, 31))
        z.DayLuTotP = np.zeros((16, z.DimYrs, 12, 31))
        z.DayLuDisN = np.zeros((16, z.DimYrs, 12, 31))
        z.DayLuDisP = np.zeros((16, z.DimYrs, 12, 31))
        z.DayErWashoff = np.zeros((16, z.DimYrs, 12, 31))
        z.Perc = np.zeros((z.DimYrs, 12, 31))
        z.DeepFlow = np.zeros((z.DimYrs, 12, 31))
        z.DayQRunoff = np.zeros((z.DimYrs, 12, 31))
        z.SdYld = np.zeros((z.DimYrs, 12, 31))
        z.Erosn = np.zeros((z.DimYrs, 12, 31))
        z.DayErosion = np.zeros((z.DimYrs, 12, 31))
        z.DayLuErosion = np.zeros((16, z.DimYrs, 12, 31))
        z.DaySed = np.zeros((z.DimYrs, 12, 31))
        z.DayLuSed = np.zeros((16, z.DimYrs, 12, 31))
        # z.DayRunoff = np.zeros((z.DimYrs, 12, 31))
        z.DayLuRunoff = np.zeros((16, z.DimYrs, 12, 31))
        # z.MeltPest = np.zeros((z.DimYrs, 12, 31))
        z.PrecPest = np.zeros((z.DimYrs, 12, 31))
        # z.DailyGrFlow = np.zeros((z.DimYrs, 12, 31))
        z.DailyETCm = np.zeros((z.DimYrs, 12, 31))
        z.DailyETShal = np.zeros((z.DimYrs, 12, 31))
        # z.PercCm = np.zeros((z.DimYrs, 12, 31))
        z.PercShal = np.zeros((z.DimYrs, 12, 31))
        z.DailyUnsatStorCm = np.zeros((z.DimYrs, 12, 31))
        z.DailyUnsatStorShal = np.zeros((z.DimYrs, 12, 31))
        z.DailyET = np.zeros((z.DimYrs, 12, 31))
        z.DailyRetent = np.zeros((z.DimYrs, 12, 31))
        z.SatStorPest = np.zeros((z.DimYrs, 12, 31))
        # z.UrbanRunoff = np.zeros((z.DimYrs, 12))
        # z.RuralRunoff = np.zeros((z.DimYrs, 12))
        z.DailyInfilt = np.zeros((z.DimYrs, 12, 31))
        # z.StreamFlowVol = np.zeros((z.DimYrs, 12))
        # z.DailyCN = np.zeros((z.DimYrs, 12, 31))
        # z.DailyWater = np.zeros((z.DimYrs, 12, 31))
        # z.LE = np.zeros((z.DimYrs, 12))
        # z.StreamBankEros = np.zeros((z.DimYrs, 12))
        # z.StreamBankN = np.zeros((z.DimYrs, 12))
        # z.StreamBankN_1 = np.zeros((z.DimYrs, 12))
        z.StreamBankP = np.zeros((z.DimYrs, 12))
        # z.DailyAMC5 = np.zeros((z.DimYrs, 12, 31))
        # z.MonthFlow = np.zeros((z.DimYrs, 12))
        z.LuGrFlow = np.zeros((16, z.DimYrs, 12, 31))
        z.LuDeepSeep = np.zeros((16, z.DimYrs, 12, 31))
        z.LuInfiltration = np.zeros((16, z.DimYrs, 12, 31))
        z.PestTemp = np.zeros((z.DimYrs, 12, 31))
        z.PestPrec = np.zeros((z.DimYrs, 12, 31))

        # Tile Drainage and Flow Variables
        z.TileDrainN = np.zeros((z.DimYrs, 12))
        z.TileDrainP = np.zeros((z.DimYrs, 12))
        z.TileDrainSed = np.zeros((z.DimYrs, 12))
        z.GroundNitr = np.zeros((z.DimYrs, 12))
        z.GroundPhos = np.zeros((z.DimYrs, 12))
        z.DisNitr = np.zeros((z.DimYrs, 12))
        z.SepticN = np.zeros((z.DimYrs, 12))
        z.SepticP = np.zeros((z.DimYrs, 12))
        z.TotNitr = np.zeros((z.DimYrs, 12))
        z.DisPhos = np.zeros((z.DimYrs, 12))
        z.TotPhos = np.zeros((z.DimYrs, 12))
        z.LuSedYield = np.zeros((z.DimYrs, 16))
        z.LuDisNitr = np.zeros((z.DimYrs, 16))
        z.LuTotNitr = np.zeros((z.DimYrs, 16))
        z.LuTotNitr_2 = np.zeros((z.DimYrs, 16))
        z.LuDisPhos = np.zeros((z.DimYrs, 16))
        z.LuTotPhos = np.zeros((z.DimYrs, 16))
        z.LuTotPhos_1 = np.zeros((z.DimYrs, 16))
        z.SepticNitr = np.zeros(z.DimYrs)
        z.SepticPhos = np.zeros(z.DimYrs)

        # ANIMAL FEEDING OPERATIONS VARIABLES
        z.DailyAnimalN = np.zeros((z.DimYrs, 12, 31))
        z.DailyAnimalP = np.zeros((z.DimYrs, 12, 31))

        # Calculated Values for Animal Feeding Operations
        z.NGLostManN = np.zeros((z.DimYrs, 12))
        z.NGLostBarnN = np.zeros((z.DimYrs, 12))
        z.NGLostManP = np.zeros((z.DimYrs, 12))
        z.NGLostBarnP = np.zeros((z.DimYrs, 12))
        z.NGLostManFC = np.zeros((z.DimYrs, 12))
        z.NGLostBarnFC = np.zeros((z.DimYrs, 12))

        # z.GRLostManN = np.zeros((z.DimYrs, 12))
        z.GRLostBarnN = np.zeros((z.DimYrs, 12))
        z.GRLossN = np.zeros((z.DimYrs, 12))
        z.GRLostManP = np.zeros((z.DimYrs, 12))
        z.GRLostBarnP = np.zeros((z.DimYrs, 12))
        z.GRLossP = np.zeros((z.DimYrs, 12))
        z.GRLostManFC = np.zeros((z.DimYrs, 12))
        z.GRLostBarnFC = np.zeros((z.DimYrs, 12))
        z.GRLossFC = np.zeros((z.DimYrs, 12))
        # z.LossFactAdj = np.zeros((z.DimYrs, 12))
        # z.AnimalN = np.zeros((z.DimYrs, 12))
        z.AnimalP = np.zeros((z.DimYrs, 12))
        z.AnimalFC = np.zeros((z.DimYrs, 12))
        z.WWOrgs = np.zeros((z.DimYrs, 12))
        z.SSOrgs = np.zeros((z.DimYrs, 12))
        z.UrbOrgs = np.zeros((z.DimYrs, 12))
        z.WildOrgs = np.zeros((z.DimYrs, 12))
        z.TotalOrgs = np.zeros((z.DimYrs, 12))
        z.CMStream = np.zeros((z.DimYrs, 12))
        z.OrgConc = np.zeros((z.DimYrs, 12))

        z.StreamBankPSum = np.zeros(z.WxYrs)
        z.StreamBankErosSum = np.zeros(z.WxYrs)
        z.StreamBankPSum = np.zeros(z.WxYrs)
        z.GroundNitrSum = np.zeros(z.WxYrs)
        z.GroundPhosSum = np.zeros(z.WxYrs)
        z.TileDrainSum = np.zeros(z.WxYrs)
        z.TileDrainNSum = np.zeros(z.WxYrs)
        z.TileDrainPSum = np.zeros(z.WxYrs)
        z.TileDrainSedSum = np.zeros(z.WxYrs)
        z.AnimalNSum = np.zeros(z.WxYrs)
        z.AnimalPSum = np.zeros(z.WxYrs)
        z.AnimalFCSum = np.zeros(z.WxYrs)
        z.WWOrgsSum = np.zeros(z.WxYrs)
        z.SSOrgsSum = np.zeros(z.WxYrs)
        z.UrbOrgsSum = np.zeros(z.WxYrs)
        z.WildOrgsSum = np.zeros(z.WxYrs)
        z.TotalOrgsSum = np.zeros(z.WxYrs)
        # z.GRLostBarnNSum = np.zeros(z.WxYrs)
        z.GRLostBarnPSum = np.zeros(z.WxYrs)
        z.GRLostBarnFCSum = np.zeros(z.WxYrs)
        # z.NGLostBarnNSum = np.zeros(z.WxYrs)
        z.NGLostBarnPSum = np.zeros(z.WxYrs)
        z.NGLostBarnFCSum = np.zeros(z.WxYrs)
        z.NGLostManPSum = np.zeros(z.WxYrs)
        z.TotNitrSum = np.zeros(z.WxYrs)
        z.TotPhosSum = np.zeros(z.WxYrs)

        # Set the Total AEU to the value from the Animal Density layer
        if not self.version_match(z.TranVersionNo, '1.[0-9].[0-9]'):
            raise Exception('Input data file is not in the correct format or is no longer supported')

        # Lines 3 - 7: (each line represents 1 day)
        # Antecedent Rain + Melt Moisture Condition for Days 1 to 5
        z.AntMoist = np.zeros(5)
        z.AntMoist_0 = np.zeros(5)

        for i in range(5):
            z.AntMoist_0[i] = self.next(float)
            self.next(EOL)

        # Lines 8 - 19: (each line represents 1 month)
        z.Month = np.zeros(12, dtype=object)
        z.KV = np.zeros(12)
        z.DayHrs = np.zeros(12)
        z.Grow_0 = np.zeros(12, dtype=object)
        z.Acoef = np.zeros(12)
        z.StreamWithdrawal = np.zeros(12)
        z.GroundWithdrawal = np.zeros(12)
        z.PcntET = np.zeros(12)

        for i in range(12):
            z.Month[i] = self.next(str)  # Month (Jan - Dec)
            z.KV[i] = self.next(float)  # KET (Flow Factor)
            z.DayHrs[i] = self.next(float)  # Day Length (hours)
            z.Grow_0[i] = self.next(GrowFlag.parse)  # Growing season flag
            z.Acoef[i] = self.next(float)  # Erosion Coefficient
            z.StreamWithdrawal[i] = self.next(float)  # Surface Water Withdrawal/Extraction
            z.GroundWithdrawal[i] = self.next(float)  # Groundwater Withdrawal/Extraction
            z.PcntET[i] = self.next(float)  # Percent monthly adjustment for ET calculation
            self.next(EOL)

        # Lines 20 - 29: (for each Rural Land Use Category)
        for i in range(z.NRur):
            z.Landuse[i] = self.next(LandUse.parse)  # Rural Land Use Category
            z.Area[i] = self.next(float)  # Area (Ha)
            z.CN[i] = self.next(float)  # Curve Number
            z.KF[i] = self.next(float)  # K Factor
            z.LS[i] = self.next(float)  # LS Factor
            z.C[i] = self.next(float)   # C Factor
            z.P[i] = self.next(float)   # P Factor
            self.next(EOL)

        # Lines 30 - 35: (for each Urban Land Use Category)
        z.Imper = np.zeros(z.NLU)
        z.TotSusSolids = np.zeros(z.NLU)

        z.CNI_0 = np.zeros((3, z.NLU))
        z.CNP_0 = np.zeros((3, z.NLU))

        for i in range(z.NRur, z.NLU):
            z.Landuse[i] = self.next(LandUse.parse)  # Urban Land Use Category
            z.Area[i] = self.next(float)  # Area (Ha)
            z.Imper[i] = self.next(float)  # Impervious Surface %
            z.CNI_0[1][i] = self.next(float)  # Curve Number(Impervious Surfaces)
            z.CNP_0[1][i] = self.next(float)  # Curve Number(Pervious Surfaces)
            z.TotSusSolids[i] = self.next(float)  # Total Suspended Solids Factor
            self.next(EOL)

        # Line 36:
        z.PhysFlag = self.next(YesOrNo.parse)  # Physiographic Province Layer Detected
        z.PointFlag = self.next(YesOrNo.parse)  # Point Source Layer Detected
        z.SeptSysFlag = self.next(YesOrNo.parse)  # Septic System Layer Detected
        z.CountyFlag = self.next(YesOrNo.parse)  # County Layer Detected
        z.SoilPFlag = self.next(YesOrNo.parse)  # Soil P Layer Detected
        z.GWNFlag = self.next(YesOrNo.parse)  # Groundwater N Layer Detected
        z.SedAAdjust = self.next(float)  # Default Percent ET
        self.next(EOL)

        # Line 37:
        z.SedNitr = self.next(float)  # Soil Concentration: N (mg/l)
        z.SedPhos = self.next(float)  # Soil Concentration: P (mg/l)
        z.GrNitrConc = self.next(float)  # Groundwater Concentration: N (mg/l)
        z.GrPhosConc = self.next(float)  # Groundwater Concentration: P (mg/l)
        z.BankNFrac = self.next(float)  # % Bank N Fraction (0 - 1)
        z.BankPFrac = self.next(float)  # % Bank P Fraction (0 - 1)
        self.next(EOL)

        # Line 38:
        z.ManuredAreas = self.next(int)  # Manure Spreading Periods (Default = 2)
        z.FirstManureMonth = self.next(int)  # MS Period 1: First Month
        z.LastManureMonth = self.next(int)  # MS Period 1: Last Month
        z.FirstManureMonth2 = self.next(int)  # MS Period 2: First Month
        z.LastManureMonth2 = self.next(int)  # MS Period 2: Last Month
        self.next(EOL)

        # Convert 1-based indexes to 0-based.
        z.FirstManureMonth -= 1
        z.FirstManureMonth2 -= 1
        z.LastManureMonth -= 1
        z.LastManureMonth2 -= 1

        # Lines 39 - 48: (for each Rural Land Use Category)
        z.NitrConc = np.zeros(16)
        z.PhosConc = np.zeros(16)

        for i in range(z.NRur):
            z.NitrConc[i] = self.next(float)  # Dissolved Runoff Coefficient: N (mg/l)
            z.PhosConc[i] = self.next(float)  # Dissolved Runoff Coefficient: P (mg/l)
            self.next(EOL)

        # Line 49:
        z.Nqual = self.next(int)  # Number of Contaminants (Default = 3; Nitrogen, Phosphorus, Sediment)
        self.next(EOL)

        # Lines 50 - 52:
        z.Contaminant = np.zeros(z.Nqual, dtype=object)
        z.SolidBasinMass = np.zeros(z.Nqual)
        z.DisBasinMass = np.zeros(z.Nqual)

        for i in range(z.Nqual):
            z.Contaminant[i] = self.next(str)
            self.next(EOL)

        # Lines 53 - 58 (for each Urban Land Use Category, Nitrogen Contaminant)
        # Lines 59 - 64: (for each Urban Land Use Category, Phosphorus Contaminant)
        # Lines 65 - 70: (for each Urban Land Use Category, Sediment Contaminant)
        z.LoadRateImp = np.zeros((z.NLU, z.Nqual))
        z.LoadRatePerv = np.zeros((z.NLU, z.Nqual))
        z.DisFract = np.zeros((z.NLU, z.Nqual))
        z.UrbBMPRed = np.zeros((z.NLU, z.Nqual))

        for u in range(z.NRur, z.NLU):
            for q in range(z.Nqual):
                z.LoadRateImp[u][q] = self.next(float)  # Loading Rate Impervious Surface
                z.LoadRatePerv[u][q] = self.next(float)  # Loading Rate Pervious Surface
                z.DisFract[u][q] = self.next(float)  # Dissolved Fraction
                z.UrbBMPRed[u][q] = self.next(float)  # Urban BMP Reduction
                self.next(EOL)

        z.ManNitr = np.zeros(z.ManuredAreas)
        z.ManPhos = np.zeros(z.ManuredAreas)

        # Lines 71 - 72: (for the 2 Manure Spreading Periods)
        for i in range(z.ManuredAreas):
            z.ManNitr[i] = self.next(float)  # Manured N Concentration
            z.ManPhos[i] = self.next(float)  # Manured P Concentration
            self.next(EOL)

        # Lines 73 - 84: (Point Source data for each Month)
        z.PointNitr = np.zeros(12)
        z.PointPhos = np.zeros(12)
        z.PointFlow = np.zeros(12)

        for i in range(12):
            z.PointNitr[i] = self.next(float)  # N Load (kg)
            z.PointPhos[i] = self.next(float)  # P Load (kg)
            z.PointFlow[i] = self.next(float)  # Discharge (Millions of Gallons per Day)
            self.next(EOL)

        # Line 85:
        z.SepticFlag = self.next(YesOrNo.parse)  # Flag: Septic Systems Layer Detected (0 No; 1 Yes)
        self.next(EOL)

        # Lines 86 - 97: (Septic System data for each Month)
        for i in range(12):
            z.NumNormalSys[i] = self.next(int)  # Number of People on Normal Systems
            z.NumPondSys[i] = self.next(int)  # Number of People on Pond Systems
            z.NumShortSys[i] = self.next(int)  # Number of People on Short Circuit Systems
            z.NumDischargeSys[i] = self.next(int)  # Number of People on Discharge Systems
            z.NumSewerSys[i] = self.next(int)  # Number of People on Public Sewer Systems
            self.next(EOL)

        # Line 98: (if Septic System flag = 1)
        if z.SepticFlag == YesOrNo.YES:
            z.NitrSepticLoad = self.next(float)  # Per Capita Tank Load: N (g/d)
            z.PhosSepticLoad = self.next(float)  # Per Capita Tank Load: P (g/d)
            z.NitrPlantUptake = self.next(float)  # Growing System Uptake: N (g/d)
            z.PhosPlantUptake = self.next(float)  # Growing System Uptake: P (g/d)
            self.next(EOL)
        else:
            raise Exception('SepticFlag must be set to 1')

        # Line 99:
        z.TileNconc = self.next(float)  # Tile Drainage Concentration: N (mg/L)
        z.TilePConc = self.next(float)  # Tile Drainage Concentration: P (mg/L)
        z.TileSedConc = self.next(float)  # Tile Drainage Concentration: Sediment (mg/L)
        self.next(EOL)

        # Line 100: (variables passed through GWLF-E to PRedICT)
        z.InName = self.next(str)  # Scenario Run Name
        z.UnitsFileFlag = self.next(int)  # Units Flag (Default = 1)
        z.AssessDate = self.next(str)  # Assessment/Reference Date (mmyyyy)
        z.VersionNo = self.next(str)  # GWLF-E Version Number
        self.next(EOL)

        # Line 101: (variable passed through GWLF-E to PRedICT)
        z.ProjName = self.next(str)  # Project Name
        self.next(EOL)

        # Line 102: (Estimated Load by Land Use/Source �� Total Sediment (kg x 1000))
        z.n1 = self.next(float)  # Row Crops
        z.n2 = self.next(float)  # Hay/Pasture
        z.n2b = self.next(float)  # High Density Urban
        z.n2c = self.next(float)  # Low Density Urban
        z.n2d = self.next(float)  # Unpaved Roads
        z.n3 = self.next(float)  # Other
        z.n4 = self.next(float)  # Streambank Erosion
        self.next(EOL)

        # Line 103: (Estimated Load by Land Use/Source �� Total Nitrogen (kg))
        z.n5 = self.next(float)  # Row Crops
        z.n6 = self.next(float)  # Hay/Pasture
        z.n6b = self.next(float)  # High Density Urban
        z.n6c = self.next(float)  # Low Density Urban
        z.n6d = self.next(float)  # Unpaved Roads
        z.n7 = self.next(float)  # Other
        # z.n7b_0 = self.next(float)  # Farm Animals
        _ = self.next(float)  # Farm Animals
        z.n8 = self.next(float)  # Streambank Erosion
        z.n9 = self.next(float)  # Groundwater/Subsurface
        z.n10 = self.next(float)  # Point Source Discharges
        z.n11 = self.next(float)  # Septic Systems
        self.next(EOL)

        # Line 104: (Estimated Load by Land Use/Source �� Total Phosphorus (kg))
        z.n12 = self.next(float)  # Row Crops
        z.n13 = self.next(float)  # Hay/Pasture
        z.n13b = self.next(float)  # High Density Urban
        z.n13c = self.next(float)  # Low Density Urban
        z.n13d = self.next(float)  # Unpaved Roads
        z.n14 = self.next(float)  # Other
        z.n14b = self.next(float)  # Farm Animals
        z.n15 = self.next(float)  # Streambank Erosion
        z.n16 = self.next(float)  # Groundwater/Subsurface
        z.n17 = self.next(float)  # Point Source Discharges
        z.n18 = self.next(float)  # Septic Systems
        self.next(EOL)

        # Line 105:
        z.n19 = self.next(float)  # Total Sediment Load (kg x 1000)
        z.n20 = self.next(float)  # Total Nitrogen Load (kg)
        z.n21 = self.next(float)  # Total Phosphorus Load (kg)
        z.n22 = self.next(float)  # Basin Area (Ha)
        self.next(EOL)

        # Line 106:
        z.n23 = self.next(float)  # Row Crops Area (Ha)
        z.n23b = self.next(float)  # High Density Urban Area (Ha)
        z.n23c = self.next(float)  # High Density Urban (Constructed Wetlands): % Drainage Used
        z.n24 = self.next(float)  # Hay/Pasture Area (Ha)
        z.n24b = self.next(float)  # Low Density Urban Area (ha Ha
        z.n24c = self.next(float)  # Low Density Urban (Constructed Wetlands): % Drainage Used
        z.n24d = self.next(float)  # High Density Urban (Bioretention Areas): % Drainage Used
        z.n24e = self.next(float)  # Low Density Urban (Bioretention Areas): % Drainage Used
        self.next(EOL)

        # Line 107:
        z.n25 = self.next(float)  # Row Crops (BMP 1): Existing (%)
        z.n25b = self.next(float)  # High Density Urban (Constructed Wetlands): Existing (%)
        z.n25c = self.next(float)  # Low Density Urban (Constructed Wetlands): Existing (%)
        z.n25d = self.next(float)  # High Density Urban (Bioretention Areas): Existing (%)
        z.n25e = self.next(float)  # Low Density Urban (Bioretention Areas): Existing (%)
        z.n26 = self.next(float)  # Row Crops (BMP 2): Existing (%)
        z.n26b = self.next(float)  # High Density Urban (Detention Basin): Existing (%)
        z.n26c = self.next(float)  # Low Density Urban (Detention Basin): Existing (%)
        z.n27 = self.next(float)  # Row Crops (BMP 3): Existing (%)
        z.n27b = self.next(float)  # Row Crops (BMP 4): Existing (%)
        z.n28 = self.next(float)  # Row Crops (BMP 5): Existing (%)
        z.n28b = self.next(float)  # Row Crops (BMP 6): Existing (%)
        z.n29 = self.next(float)  # Row Crops (BMP 8): Existing (%)
        self.next(EOL)

        # Line 108:
        z.n30 = self.next(float)  # Row Crops (BMP 1): Future (%)
        z.n30b = self.next(float)  # High Density Urban (Constructed Wetlands): Future (%)
        z.n30c = self.next(float)  # Low Density Urban (Constructed Wetlands): Future (%)
        z.n30d = self.next(float)  # High Density Urban (Bioretention Areas): Future (%)
        z.n30e = self.next(float)  # Low Density Urban (Bioretention Areas): Future (%)
        z.n31 = self.next(float)  # Row Crops (BMP 2): Future (%)
        z.n31b = self.next(float)  # High Density Urban (Detention Basin): Future (%)
        z.n31c = self.next(float)  # Low Density Urban (Detention Basin): Future (%)
        z.n32 = self.next(float)  # Row Crops (BMP 3): Future (%)
        z.n32b = self.next(float)  # Row Crops (BMP 4): Future (%)
        z.n32c = self.next(float)  # Hay/Pasture (BMP 3): Existing (%)
        z.n32d = self.next(float)  # Hay/Pasture (BMP 3): Future (%)
        z.n33 = self.next(float)  # Row Crops (BMP 5): Future (%)
        z.n33b = self.next(float)  # Row Crops (BMP 6): Future (%)
        z.n33c = self.next(float)  # Hay/Pasture (BMP 4): Existing (%)
        z.n33d = self.next(float)  # Hay/Pasture (BMP 4): Future (%)
        self.next(EOL)

        # Line 109:
        z.n34 = self.next(float)  # Row Crops (BMP 8): Future (%)
        z.n35 = self.next(float)  # Hay/Pasture (BMP 5): Existing (%)
        z.n35b = self.next(float)  # Hay/Pasture (BMP 6): Existing (%)
        z.n36 = self.next(float)  # Hay/Pasture (BMP 7): Existing (%)
        z.n37 = self.next(float)  # Hay/Pasture (BMP 8): Existing (%)
        z.n38 = self.next(float)  # Hay/Pasture (BMP 5): Future (%)
        z.n38b = self.next(float)  # Hay/Pasture (BMP 6): Future (%)
        z.n39 = self.next(float)  # Hay/Pasture (BMP 7): Future (%)
        z.n40 = self.next(float)  # Hay/Pasture (BMP 8): Future (%)
        self.next(EOL)

        # Line 110:
        z.n41 = self.next(float)  # Agricultural Land on Slope > 3% (Ha)
        z.n41b = self.next(float)  # AWMS (Livestock): Existing (%)
        z.n41c = self.next(float)  # AWMS (Livestock): Future (%)
        z.n41d = self.next(float)  # AWMS (Poultry): Existing (%)
        z.n41e = self.next(float)  # AWMS (Poultry): Future (%)
        z.n41f = self.next(float)  # Runoff Control: Existing (%)
        z.n41g = self.next(float)  # Runoff Control: Future (%)
        z.n41h = self.next(float)  # Phytase in Feed: Existing (%)
        z.n41i = self.next(float)  # Phytase in Feed: Future (%)
        z.n41j = self.next(float)  # Total Livestock AEUs
        z.n41k = self.next(float)  # Total Poultry AEUs
        z.n41l = self.next(float)  # Total AEUs
        z.n42 = self.next(float)  # Streams in Agricultural Areas (km)
        z.n42b = self.next(float)  # Total Stream Length (km)
        z.n42c = self.next(float)  # Unpaved Road Length (km)
        z.n43 = self.next(float)  # Stream Km with Vegetated Buffer Strips: Existing
        # z.GRLBN = self.next(float)  # Average Grazing Animal Loss Rate (Barnyard/Confined Area): Nitrogen
        _ = self.next(float)  # Average Grazing Animal Loss Rate (Barnyard/Confined Area): Nitrogen
        # z.NGLBN = self.next(float)  # Average Non-Grazing Animal Loss Rate (Barnyard/Confined Area): Nitrogen
        _ = self.next(float)  # Average Non-Grazing Animal Loss Rate (Barnyard/Confined Area): Nitrogen
        z.GRLBP = self.next(float)  # Average Grazing Animal Loss Rate (Barnyard/Confined Area): Phosphorus
        z.NGLBP = self.next(float)  # Average Non-Grazing Animal Loss Rate (Barnyard/Confined Area): Phosphorus
        z.NGLManP = self.next(float)  # Average Non-Grazing Animal Loss Rate (Manure Spreading): Phosphorus
        z.NGLBFC = self.next(float)  # Average Non-Grazing Animal Loss Rate (Barnyard/Confined Area): Fecal Coliform
        z.GRLBFC = self.next(float)  # Average Grazing Animal Loss Rate (Barnyard/Confined Area): Fecal Coliform
        z.GRSFC = self.next(float)  # Average Grazing Animal Loss Rate (Spent in Streams): Fecal Coliform
        # z.GRSN = self.next(float)  # Average Grazing Animal Loss Rate (Spent in Streams): Nitrogen
        _ = self.next(float)  # Value set before it is used
        z.GRSP = self.next(float)  # Average Grazing Animal Loss Rate (Spent in Streams): Phosphorus
        self.next(EOL)

        # Line 111:
        z.n43b = self.next(float)  # High Density Urban (Constructed Wetlands): Required Ha
        z.n43c = self.next(float)  # High Density Urban (Detention Basin): % Drainage Used
        z.n43d = self.next(float)  # High Density Urban: % Impervious Surface
        z.n43e = self.next(float)  # High Density Urban (Constructed Wetlands): Impervious Ha Drained
        z.n43f = self.next(float)  # High Density Urban (Detention Basin): Impervious Ha Drained
        z.n43g = self.next(float)  # High Density Urban (Bioretention Areas): Impervious Ha Drained
        z.n43h = self.next(float)  # High Density Urban (Bioretention Areas): Required Ha
        z.n43i = self.next(float)  # Low Density Urban (Bioretention Areas): Impervious Ha Drained
        z.n43j = self.next(float)  # Low Density Urban (Bioretention Areas): Required Ha
        z.n44 = self.next(float)  # Stream Km with Vegetated Buffer Strips: Future
        z.n44b = self.next(float)  # High Density Urban (Detention Basin): Required Ha
        z.n45 = self.next(float)  # Stream Km with Fencing: Existing
        z.n45b = self.next(float)  # Low Density Urban (Constructed Wetlands): Required Ha
        z.n45c = self.next(float)  # Low Density Urban (Detention Basin): % Drainage Used
        z.n45d = self.next(float)  # Low Density Urban: % Impervious Surface
        z.n45e = self.next(float)  # Low Density Urban (Constructed Wetlands): Impervious Ha Drained
        z.n45f = self.next(float)  # Low Density Urban (Detention Basin): Impervious Ha Drained
        self.next(EOL)

        # Line 112:
        z.n46 = self.next(float)  # Stream Km with Fencing: Future
        z.n46b = self.next(float)  # Low Density Urban (Detention Basin): Required Ha
        z.n46c = self.next(float)  # Stream Km with Stabilization: Existing
        z.n46d = self.next(float)  # Stream Km with Stabilization: Future
        z.n46e = self.next(float)  # Stream Km in High Density Urban Areas
        z.n46f = self.next(float)  # Stream Km in Low Density Urban Areas
        z.n46g = self.next(float)  # Stream Km in High Density Urban Areas W/Buffers: Existing
        z.n46h = self.next(float)  # Stream Km in High Density Urban Areas W/Buffers: Future
        z.n46i = self.next(float)  # High Density Urban Streambank Stabilization (km): Existing
        z.n46j = self.next(float)  # High Density Urban Streambank Stabilization (km): Future
        z.n46k = self.next(float)  # Stream Km in Low Density Urban Areas W/Buffers: Existing
        z.n46l = self.next(float)  # Stream Km in Low Density Urban Areas W/Buffers: Future
        z.n46m = self.next(float)  # Low Density Urban Streambank Stabilization (km): Existing
        z.n46n = self.next(float)  # Low Density Urban Streambank Stabilization (km): Future
        z.n46o = self.next(float)  # Unpaved Road Km with E and S Controls (km): Existing
        z.n46p = self.next(float)  # Unpaved Road Km with E and S Controls (km): Future
        self.next(EOL)

        # Line 113:
        z.n47 = self.next(float)  # Number of Persons on Septic Systems: Existing
        z.n48 = self.next(float)  # No longer used (Default = 0)
        z.n49 = self.next(float)  # Number of Persons on Septic Systems: Future
        z.n50 = self.next(float)  # No longer used (Default = 0)
        z.n51 = self.next(float)  # Septic Systems Converted by Secondary Treatment Type (%)
        z.n52 = self.next(float)  # Septic Systems Converted by Tertiary Treatment Type (%)
        z.n53 = self.next(float)  # No longer used (Default = 0)
        z.n54 = self.next(float)  # Distribution of Pollutant Discharges by Primary Treatment Type (%): Existing
        z.n55 = self.next(float)  # Distribution of Pollutant Discharges by Secondary Treatment Type (%): Existing
        z.n56 = self.next(float)  # Distribution of Pollutant Discharges by Tertiary Treatment Type (%): Existing
        z.n57 = self.next(float)  # Distribution of Pollutant Discharges by Primary Treatment Type (%): Future
        z.n58 = self.next(float)  # Distribution of Pollutant Discharges by Secondary Treatment Type (%): Future
        z.n59 = self.next(float)  # Distribution of Pollutant Discharges by Tertiary Treatment Type (%): Future
        z.n60 = self.next(float)  # Distribution of Treatment Upgrades (%): Primary to Secondary
        z.n61 = self.next(float)  # Distribution of Treatment Upgrades (%): Primary to Tertiary
        z.n62 = self.next(float)  # Distribution of Treatment Upgrades (%): Secondary to Tertiary
        self.next(EOL)

        # Line 114: (BMP Load Reduction Efficiencies)
        z.n63 = self.next(float)  # BMP 1 (Nitrogen)
        z.n64 = self.next(float)  # Vegetated Buffer Strips (Nitrogen)
        z.n65 = self.next(float)  # BMP 2 (Nitrogen)
        z.n66 = self.next(float)  # BMP 3 (Nitrogen)
        z.n66b = self.next(float)  # BMP 4 (Nitrogen)
        z.n67 = self.next(float)  # BMP 5 (Nitrogen)
        z.n68 = self.next(float)  # BMP 8 (Nitrogen)
        z.n68b = self.next(float)  # BMP 7 (Nitrogen)
        z.n69 = self.next(float)  # Streambank Fencing (Nitrogen)
        z.n69b = self.next(float)  # Constructed Wetlands (Nitrogen)
        z.n69c = self.next(float)  # Streambank Stabilization (Nitrogen)
        z.n70 = self.next(float)  # BMP 6 (Nitrogen)
        z.n70b = self.next(float)  # Detention Basins (Nitrogen)
        self.next(EOL)

        # Line 115: (BMP Load Reduction Efficiencies cont.)
        z.n71 = self.next(float)  # BMP 1 (Phosphorus)
        z.n71b = self.next(float)  # Bioretention Areas (Nitrogen)
        z.n72 = self.next(float)  # Vegetated Buffer Strips (Phosphorus)
        z.n73 = self.next(float)  # BMP 2 (Phosphorus)
        z.n74 = self.next(float)  # BMP 3 (Phosphorus)
        z.n74b = self.next(float)  # BMP 4 (Phosphorus)
        z.n75 = self.next(float)  # BMP 5 (Phosphorus)
        z.n76 = self.next(float)  # BMP 8 (Phosphorus)
        z.n76b = self.next(float)  # BMP 7 (Phosphorus)
        z.n77 = self.next(float)  # Streambank Fencing (Phosphorus)
        z.n77b = self.next(float)  # Constructed Wetlands (Phosphorus)
        z.n77c = self.next(float)  # Streambank Stabilization (Phosphorus)
        z.n78 = self.next(float)  # BMP 6 (Phosphorus)
        z.n78b = self.next(float)  # Detention Basins (Phosphorus)
        self.next(EOL)

        # Line 116: (BMP Load Reduction Efficiencies cont.)
        z.n79 = self.next(float)  # BMP 1 (Sediment)
        z.n79b = self.next(float)  # Bioretention Areas (Phosphorus)
        z.n79c = self.next(float)  # Bioretention Areas (Sediment)
        z.n80 = self.next(float)  # Vegetated Buffer Strips (Sediment)
        z.n81 = self.next(float)  # BMP 2 (Sediment)
        z.n82 = self.next(float)  # BMP 3 (Sediment)
        z.n82b = self.next(float)  # BMP 4 (Sediment)
        z.n83 = self.next(float)  # BMP 5 (Sediment)
        z.n84 = self.next(float)  # BMP 8 (Sediment)
        z.n84b = self.next(float)  # BMP 7 (Sediment)
        z.n85 = self.next(float)  # Streambank Fencing (Sediment)
        z.n85b = self.next(float)  # Constructed Wetlands (Sediment)
        z.n85c = self.next(float)  # Detention Basins (Sediment)
        z.n85d = self.next(float)  # Streambank Stabilization (Sediment)
        z.n85e = self.next(float)  # Unpaved Road (kg/meter) (Nitrogen)
        z.n85f = self.next(float)  # Unpaved Road (kg/meter) (Phosphorus)
        z.n85g = self.next(float)  # Unpaved Road (kg/meter) (Sediment)
        self.next(EOL)

        # Line 117: (BMP Load Reduction Efficiencies cont.)
        z.n85h = self.next(float)  # AWMS (Livestock) (Nitrogen)
        z.n85i = self.next(float)  # AWMS (Livestock) (Phosphorus)
        z.n85j = self.next(float)  # AWMS (Poultry) (Nitrogen)
        z.n85k = self.next(float)  # AWMS (Poultry) (Phosphorus)
        z.n85l = self.next(float)  # Runoff Control (Nitrogen)
        z.n85m = self.next(float)  # Runoff Control (Phosphorus)
        z.n85n = self.next(float)  # Phytase in Feed (Phosphorus)
        z.n85o = self.next(float)  # Vegetated Buffer Strips (Pathogens)
        z.n85p = self.next(float)  # Streambank Fencing (Pathogens)
        z.n85q = self.next(float)  # AWMS (Livestock) (Pathogens)
        z.n85r = self.next(float)  # AWMS (Poultry) (Pathogens)
        z.n85s = self.next(float)  # Runoff Control (Pathogens)
        z.n85t = self.next(float)  # Constructed Wetlands (Pathogens)
        z.n85u = self.next(float)  # Bioretention Areas (Pathogens)
        z.n85v = self.next(float)  # Detention Basins (Pathogens)
        self.next(EOL)

        # Line 118: (Wastewater Discharge BMP Reduction Efficiencies)
        z.n86 = self.next(float)  # Conversion of Septic System to Secondary Treatment Plant (Nitrogen)
        z.n87 = self.next(float)  # Conversion of Septic System to Tertiary Treatment Plant (Nitrogen)
        z.n88 = self.next(float)  # Conversion of Primary System to Secondary Treatment Plant (Nitrogen)
        z.n89 = self.next(float)  # Conversion of Primary System to Tertiary Treatment Plant (Nitrogen)
        z.n90 = self.next(float)  # Conversion of Secondary System to Tertiary Treatment Plant (Nitrogen)
        z.n91 = self.next(float)  # Conversion of Septic System to Secondary Treatment Plant (Phosphorus)
        z.n92 = self.next(float)  # Conversion of Septic System to Tertiary Treatment Plant (Phosphorus)
        z.n93 = self.next(float)  # Conversion of Primary System to Secondary Treatment Plant (Phosphorus)
        z.n94 = self.next(float)  # Conversion of Primary System to Tertiary Treatment Plant (Phosphorus)
        z.n95 = self.next(float)  # Conversion of Secondary System to Tertiary Treatment Plant (Phosphorus)
        z.n95b = self.next(float)  # Conversion of Septic System to Secondary Treatment Plant (Pathogens)
        z.n95c = self.next(float)  # Conversion of Septic System to Tertiary Treatment Plant (Pathogens)
        z.n95d = self.next(float)  # Wastewater Treatment Plants Pathogen Distribution (cfu/100mL): Existing
        z.n95e = self.next(float)  # Wastewater Treatment Plants Pathogen Distribution (cfu/100mL): Future
        self.next(EOL)

        # Line 119: (BMP Costs $)
        z.n96 = self.next(float)  # Conservation Tillage (per Ha)
        z.n97 = self.next(float)  # Cover Crops (per Ha)
        z.n98 = self.next(float)  # Grazing Land Management (per Ha)
        z.n99 = self.next(float)  # Streambank Fencing (per km)
        z.n99b = self.next(float)  # Strip Cropping/Contour Farming (per Ha)
        z.n99c = self.next(float)  # Constructed Wetlands (per impervious Ha drained)
        z.n99d = self.next(float)  # Streambank Stabilization (per meter)
        z.n99e = self.next(float)  # Bioretention Areas (per impervious Ha drained)
        z.n100 = self.next(float)  # Vegetated Buffer Strip (per Km)
        z.n101 = self.next(float)  # Agricultural Land Retirement (per Ha)
        z.n101b = self.next(float)  # AWMS/Livestock (per AEU)
        z.n101c = self.next(float)  # AWMS/Poultry (per AEU)
        z.n101d = self.next(float)  # Runoff Control (per AEU)
        z.n101e = self.next(float)  # Phytase in Feed (per AEU)
        z.n102 = self.next(float)  # Nutrient Management (per Ha)
        z.n103a = self.next(float)  # User Defined (per Ha)
        z.n103b = self.next(float)  # Detention Basins (per impervious Ha drained)
        z.n103c = self.next(float)  # Conservation Plan (per Ha)
        z.n103d = self.next(float)  # Unpaved Roads (per meter)
        self.next(EOL)

        # Line 120:
        z.n104 = self.next(
            float)  # BMP Costs $: Conversion of Septic Systems to Centralized Sewage Treatment (per home)
        z.n105 = self.next(float)  # BMP Costs $: Conversion from Primary to Secondary Sewage Treatment (per capita)
        z.n106 = self.next(float)  # BMP Costs $: Conversion from Primary to Tertiary Sewage Treatment (per capita)
        z.n106b = self.next(float)  # No longer used (Default = 0)
        z.n106c = self.next(float)  # No longer used (Default = 0)
        z.n106d = self.next(float)  # No longer used (Default = 0)
        z.n107 = self.next(float)  # BMP Costs $: Conversion from Secondary to Tertiary Sewage Treatment (per capita)
        z.n107b = self.next(float)  # No longer used (Default = 0)
        z.n107c = self.next(float)  # No longer used (Default = 0)
        z.n107d = self.next(float)  # No longer used (Default = 0)
        z.n107e = self.next(float)  # No longer used (Default = 0)

        if self.version_match(z.TranVersionNo, '1.[0-2].[0-9]'):
            z.Storm = 0
            z.CSNAreaSim = 0
            z.CSNDevType = "None"
        else:
            z.Storm = self.next(float)  # CSN Tool: Storm Event Simulated (cm)
            z.CSNAreaSim = self.next(float)  # CSN Tool: Area Simulated (Ha)
            z.CSNDevType = self.next(str)  # CSN Tool: Development Type

        self.next(EOL)

        # Line 121:
        z.Qretention = self.next(float)  # Detention Basin: Amount of runoff retention (cm)
        z.FilterWidth = self.next(float)  # Stream Protection: Vegetative buffer strip width (meters)
        z.Capacity = self.next(float)  # Detention Basin: Detention basin volume (cubic meters)
        z.BasinDeadStorage = self.next(float)  # Detention Basin: Basin dead storage (cubic meters)
        z.BasinArea = self.next(float)  # Detention Basin: Basin surface area (square meters)
        z.DaysToDrain = self.next(float)  # Detention Basin: Basin days to drain
        z.CleanMon = self.next(float)  # Detention Basin: Basin cleaning month
        z.PctAreaInfil = self.next(float)  # Infiltration/Bioretention: Fraction of area treated (0-1)
        z.PctStrmBuf = self.next(float)  # Stream Protection: Fraction of streams treated (0-1)
        z.UrbBankStab = self.next(float)  # Stream Protection: Streams w/bank stabilization (km)

        z.ISRR = np.zeros(6)
        z.ISRA = np.zeros(6)
        z.ISRR[0] = self.next(float)  # Impervious Surface Reduction: Low Density Mixed (% Reduction)
        z.ISRA[0] = self.next(float)  # Impervious Surface Reduction: Low Density Mixed (% Area)
        z.ISRR[1] = self.next(float)  # Impervious Surface Reduction: Medium Density Mixed (% Reduction)
        z.ISRA[1] = self.next(float)  # Impervious Surface Reduction: Medium Density Mixed (% Area)
        z.ISRR[2] = self.next(float)  # Impervious Surface Reduction: High Density Mixed (% Reduction)
        z.ISRA[2] = self.next(float)  # Impervious Surface Reduction: High Density Mixed (% Area)
        z.ISRR[3] = self.next(float)  # Impervious Surface Reduction: Low Density Residential (% Reduction)
        z.ISRA[3] = self.next(float)  # Impervious Surface Reduction: Low Density Residential (% Area)
        z.ISRR[4] = self.next(float)  # Impervious Surface Reduction: Medium Density Residential (% Reduction)
        z.ISRA[4] = self.next(float)  # Impervious Surface Reduction: Medium Density Residential (% Area)
        z.ISRR[5] = self.next(float)  # Impervious Surface Reduction: High Density Residential (% Reduction)
        z.ISRA[5] = self.next(float)  # Impervious Surface Reduction: High Density Residential (% Area)

        if self.version_match(z.TranVersionNo, '1.[0-3].[0-9]'):
            z.SweepType = SweepType.MECHANICAL
            z.UrbSweepFrac = 1
        else:
            z.SweepType = self.next(SweepType.parse)  # Street Sweeping: Sweep Type (1-2)
            z.UrbSweepFrac = self.next(float)  # Street Sweeping: Fraction of area treated (0-1)

        self.next(EOL)

        # Lines 122 - 133: (Street Sweeping data for each Month)
        z.StreetSweepNo = np.zeros(12)

        for i in range(12):
            z.StreetSweepNo[i] = self.next(float)  # Street sweeping times per month
            self.next(EOL)

        # Line 134:
        z.OutName = self.next(str)  # PRedICT Output Name
        self.next(EOL)

        # Line 135: (Estimated Reduced Load)
        z.n108 = self.next(float)  # Row Crops: Sediment (kg x 1000)
        z.n109 = self.next(float)  # Row Crops: Nitrogen (kg)
        z.n110 = self.next(float)  # Row Crops: Phosphorus (kg)
        self.next(EOL)

        # Line 136: (Estimated Reduced Load)
        z.n111 = self.next(float)  # Hay/Pasture: Sediment (kg x 1000)
        z.n111b = self.next(float)  # High Density Urban: Sediment (kg x 1000)
        z.n111c = self.next(float)  # Low Density Urban: Sediment (kg x 1000)
        z.n111d = self.next(float)  # Unpaved Roads: Sediment (kg x 1000)
        z.n112 = self.next(float)  # Hay/Pasture: Nitrogen (kg)
        z.n112b = self.next(float)  # High Density Urban: Nitrogen (kg)
        z.n112c = self.next(float)  # Low Density Urban: Nitrogen (kg)
        z.n112d = self.next(float)  # Unpaved Roads: Nitrogen (kg)
        z.n113 = self.next(float)  # Hay/Pasture: Phosphorus (kg)
        z.n113b = self.next(float)  # High Density Urban: Phosphorus (kg)
        z.n113c = self.next(float)  # Low Density Urban: Phosphorus (kg)
        z.n113d = self.next(float)  # Unpaved Roads: Phosphorus (kg)
        self.next(EOL)

        # Line 137: (Estimated Reduced Load)
        z.n114 = self.next(float)  # Other: Sediment (kg x 1000)
        z.n115 = self.next(float)  # Other: Nitrogen (kg)
        z.n115b = self.next(float)  # Farm Animals: Nitrogen (kg)
        z.n116 = self.next(float)  # Other: Phosphorus (kg)
        z.n116b = self.next(float)  # Farm Animals: Phosphorus (kg)
        self.next(EOL)

        # Line 138: (Estimated Reduced Load)
        z.n117 = self.next(float)  # Streambank Erosion: Sediment (kg x 1000)
        z.n118 = self.next(float)  # Streambank Erosion: Nitrogen (kg)
        z.n119 = self.next(float)  # Streambank Erosion: Phosphorus (kg)
        self.next(EOL)

        # Line 139: (Estimated Reduced Load)
        z.n120 = self.next(float)  # Groundwater/Subsurface: Nitrogen (kg)
        z.n121 = self.next(float)  # Groundwater/Subsurface: Phosphorus (kg)
        self.next(EOL)

        # Line 140: (Estimated Reduced Load)
        z.n122 = self.next(float)  # Point Source Discharges: Nitrogen (kg)
        z.n123 = self.next(float)  # Point Source Discharges: Phosphorus (kg)
        self.next(EOL)

        # Line 141: (Estimated Reduced Load)
        z.n124 = self.next(float)  # Septic Systems: Nitrogen (kg)
        z.n125 = self.next(float)  # Septic Systems: Phosphorus (kg)
        self.next(EOL)

        # Line 142: (Estimated Reduced Load)
        z.n126 = self.next(float)  # Total: Sediment (kg x 1000)
        z.n127 = self.next(float)  # Total: Nitrogen (kg)
        z.n128 = self.next(float)  # Total: Phosphorus (kg)
        self.next(EOL)

        # Line 143: (Estimated Reduced Load)
        z.n129 = self.next(float)  # Percent Reduction: Sediment (%)
        z.n130 = self.next(float)  # Percent Reduction: Nitrogen (%)
        z.n131 = self.next(float)  # Percent Reduction: Phosphorus (%)
        self.next(EOL)

        # Line 144:
        z.n132 = self.next(float)  # Estimated Scenario Cost $: Total
        z.n133 = self.next(float)  # Estimated Scenario Cost $: Agricultural BMPs
        z.n134 = self.next(float)  # Estimated Scenario Cost $: Waste Water Upgrades
        z.n135 = self.next(float)  # Estimated Scenario Cost $: Urban BMPs
        z.n136 = self.next(float)  # Estimated Scenario Cost $: Stream Protection
        z.n137 = self.next(float)  # Estimated Scenario Cost $: Unpaved Road Protection
        z.n138 = self.next(float)  # Estimated Scenario Cost $: Animal BMPs
        z.n139 = self.next(float)  # Pathogen Loads (Farm Animals): Existing (orgs/month)
        z.n140 = self.next(float)  # Pathogen Loads (Wastewater Treatment Plants): Existing (orgs/month)
        self.next(EOL)

        # Line 145:
        z.n141 = self.next(float)  # Pathogen Loads (Septic Systems): Existing (orgs/month)
        z.n142 = self.next(float)  # Pathogen Loads (Urban Areas): Existing (orgs/month)
        z.n143 = self.next(float)  # Pathogen Loads (Wildlife): Existing (orgs/month)
        z.n144 = self.next(float)  # Pathogen Loads (Total): Existing (orgs/month)
        z.n145 = self.next(float)  # Pathogen Loads (Farm Animals): Future (orgs/month)
        z.n146 = self.next(float)  # Pathogen Loads (Wastewater Treatment Plants): Future (orgs/month)
        z.n147 = self.next(float)  # Pathogen Loads (Septic Systems): Future (orgs/month)
        z.n148 = self.next(float)  # Pathogen Loads (Urban Areas): Future (orgs/month)
        z.n149 = self.next(float)  # Pathogen Loads (Wildlife): Future (orgs/month)
        z.n150 = self.next(float)  # Pathogen Loads (Total): Future (orgs/month)
        z.n151 = self.next(float)  # Pathogen Loads: Percent Reduction (%)
        self.next(EOL)

        # Line 146:
        # z.InitNgN = self.next(float)  # Initial Non-Grazing Animal Totals: Nitrogen (kg/yr)
        _ = self.next(float)  # Seems to be set to 0 before it is used
        z.InitNgP = self.next(float)  # Initial Non-Grazing Animal Totals: Phosphorus (kg/yr)
        z.InitNgFC = self.next(float)  # Initial Non-Grazing Animal Totals: Fecal Coliforms (orgs/yr)
        z.NGAppSum = self.next(float)  # Non-Grazing Manure Data Check: Land Applied (%)
        z.NGBarnSum = self.next(float)  # Non-Grazing Manure Data Check: In Confined Areas (%)
        z.NGTotSum = self.next(float)  # Non-Grazing Manure Data Check: Total (<= 1)
        # z.InitGrN = self.next(float)  # Initial Grazing Animal Totals: Nitrogen (kg/yr)
        _ = self.next(float)  # Value seems to be set to 0 before it is used
        z.InitGrP = self.next(float)  # Initial Grazing Animal Totals: Phosphorus (kg/yr)
        z.InitGrFC = self.next(float)  # Initial Grazing Animal Totals: Fecal Coliforms (orgs/yr)
        z.GRAppSum = self.next(float)  # Grazing Manure Data Check: Land Applied (%)
        z.GRBarnSum = self.next(float)  # Grazing Manure Data Check: In Confined Areas (%)
        z.GRTotSum = self.next(float)  # Grazing Manure Data Check: Total (<= 1)
        z.AnimalFlag = self.next(YesOrNo.parse)  # Flag: Animal Layer Detected (0 No; 1 Yes)
        self.next(EOL)

        # Line 147:
        z.WildOrgsDay = self.next(float)  # Wildlife Loading Rate (org/animal/per day)
        z.WildDensity = self.next(float)  # Wildlife Density (animals/square mile)
        z.WuDieoff = self.next(float)  # Wildlife/Urban Die-Off Rate
        z.UrbEMC = self.next(float)  # Urban EMC (org/100ml)
        z.SepticOrgsDay = self.next(float)  # Septic Loading Rate (org/person per day)
        z.SepticFailure = self.next(float)  # Malfunctioning System Rate (0 - 1)
        z.WWTPConc = self.next(float)  # Wastewater Treatment Plants Loading Rate (cfu/100ml)
        z.InstreamDieoff = self.next(float)  # In-Stream Die-Off Rate
        z.AWMSGrPct = self.next(float)  # Animal Waste Management Systems: Livestock (%)
        z.AWMSNgPct = self.next(float)  # Animal Waste Management Systems: Poultry (%)
        z.RunContPct = self.next(float)  # Runoff Control (%)
        z.PhytasePct = self.next(float)  # Phytase in Feed (%)
        self.next(EOL)

        # Line 148-156: (For each Animal type)
        z.AnimalName = np.zeros(z.NAnimals, dtype=object)
        z.NumAnimals = np.zeros(z.NAnimals, dtype=int)
        z.GrazingAnimal_0 = np.zeros(z.NAnimals, dtype=object)
        z.AvgAnimalWt = np.zeros(z.NAnimals)
        z.AnimalDailyN = np.zeros(z.NAnimals)
        z.AnimalDailyP = np.zeros(z.NAnimals)
        z.FCOrgsPerDay = np.zeros(z.NAnimals)

        for i in range(z.NAnimals):
            z.AnimalName[i] = self.next(str)  # Animal Name
            z.NumAnimals[i] = self.next(int)  # Number of Animals
            z.GrazingAnimal_0[i] = self.next(YesOrNo.parse)  # Flag: Grazing Animal (��N�� No, ��Y�� Yes)
            z.AvgAnimalWt[i] = self.next(float)  # Average Animal Weight (kg)
            z.AnimalDailyN[i] = self.next(float)  # Animal Daily Loads: Nitrogen (kg/AEU)
            z.AnimalDailyP[i] = self.next(float)  # Animal Daily Loads: Phosphorus (kg/AEU)
            z.FCOrgsPerDay[i] = self.next(float)  # Fecal Coliforms (orgs/day)
            self.next(EOL)

        # Line 157-168: (For each month: Non-Grazing Animal Worksheet values)
        z.NGPctManApp = np.zeros(12)
        z.NGAppNRate = np.zeros(12)
        z.NGAppPRate = np.zeros(12)
        z.NGAppFCRate = np.zeros(12)
        z.NGPctSoilIncRate = np.zeros(12)
        z.NGBarnNRate = np.zeros(12)
        z.NGBarnPRate = np.zeros(12)
        z.NGBarnFCRate = np.zeros(12)

        for i in range(12):
            z.Month[i] = self.next(str)  # Month (Jan-Dec)
            z.NGPctManApp[i] = self.next(float)  # Manure Spreading: % Of Annual Load Applied To Crops/Pasture
            z.NGAppNRate[i] = self.next(float)  # Manure Spreading: Base Nitrogen Loss Rate
            z.NGAppPRate[i] = self.next(float)  # Manure Spreading: Base Phosphorus Loss Rate
            z.NGAppFCRate[i] = self.next(float)  # Manure Spreading: Base Fecal Coliform Loss Rate
            z.NGPctSoilIncRate[i] = self.next(float)  # Manure Spreading: % Of Manure Load Incorporated Into Soil
            z.NGBarnNRate[i] = self.next(float)  # Barnyard/Confined Area: Base Nitrogen Loss Rate
            z.NGBarnPRate[i] = self.next(float)  # Barnyard/Confined Area: Base Phosphorus Loss Rate
            z.NGBarnFCRate[i] = self.next(float)  # Barnyard/Confined Area: Base Fecal Coliform Loss Rate
            self.next(EOL)

        # Line 169-180: (For each month: Grazing Animal Worksheet values)
        z.PctGrazing = np.zeros(12)
        z.PctStreams = np.zeros(12)
        z.GrazingNRate = np.zeros(12)
        z.GrazingPRate = np.zeros(12)
        z.GrazingFCRate = np.zeros(12)
        z.GRPctManApp = np.zeros(12)
        z.GRAppNRate = np.zeros(12)
        z.GRAppPRate = np.zeros(12)
        z.GRAppFCRate = np.zeros(12)
        z.GRPctSoilIncRate = np.zeros(12)
        z.GRBarnNRate = np.zeros(12)
        z.GRBarnPRate = np.zeros(12)
        z.GRBarnFCRate = np.zeros(12)

        for i in range(12):
            z.Month[i] = self.next(str)  # Month (Jan-Dec)
            z.PctGrazing[i] = self.next(float)  # Grazing Land: % Of Time Spent Grazing
            z.PctStreams[i] = self.next(float)  # Grazing Land: % Of Time Spent In Streams
            z.GrazingNRate[i] = self.next(float)  # Grazing Land: Base Nitrogen Loss Rate
            z.GrazingPRate[i] = self.next(float)  # Grazing Land: Base Phosphorus Loss Rate
            z.GrazingFCRate[i] = self.next(float)  # Grazing Land: Base Fecal Coliform Loss Rate
            z.GRPctManApp[i] = self.next(float)  # Manure Spreading: % Of Annual Load Applied To Crops/Pasture
            z.GRAppNRate[i] = self.next(float)  # Manure Spreading: Base Nitrogen Loss Rate
            z.GRAppPRate[i] = self.next(float)  # Manure Spreading: Base Phosphorus Loss Rate
            z.GRAppFCRate[i] = self.next(float)  # Manure Spreading: Base Fecal Coliform Loss Rate
            z.GRPctSoilIncRate[i] = self.next(float)  # Manure Spreading: % Of Manure Load Incorporated Into Soil
            z.GRBarnNRate[i] = self.next(float)  # Barnyard/Confined Area: Base Nitrogen Loss Rate
            z.GRBarnPRate[i] = self.next(float)  # Barnyard/Confined Area: Base Phosphorus Loss Rate
            z.GRBarnFCRate[i] = self.next(float)  # Barnyard/Confined Area: Base Fecal Coliform Loss Rate
            self.next(EOL)

        # Line 181: (Nutrient Retention data)
        z.ShedAreaDrainLake = self.next(
            float)  # Percentage of watershed area that drains into a lake or wetlands: (0 - 1)
        z.RetentNLake = self.next(float)  # Lake Retention Rate: Nitrogen
        z.RetentPLake = self.next(float)  # Lake Retention Rate: Phosphorus
        z.RetentSedLake = self.next(float)  # Lake Retention Rate: Sediment
        z.AttenFlowDist = self.next(float)  # Attenuation: Flow Distance (km)
        z.AttenFlowVel = self.next(float)  # Attenuation: Flow Velocity (km/hr)
        z.AttenLossRateN = self.next(float)  # Attenuation: Loss Rate: Nitrogen
        z.AttenLossRateP = self.next(float)  # Attenuation: Loss Rate: Phosphorus
        z.AttenLossRateTSS = self.next(float)  # Attenuation: Loss Rate: Total Suspended Solids
        z.AttenLossRatePath = self.next(float)  # Attenuation: Loss Rate: Pathogens
        z.StreamFlowVolAdj = self.next(float)  # Streamflow Volume Adjustment Factor
        self.next(EOL)

        # Line 182 �� Last Weather Day: (Weather data)
        z.DaysMonth = np.zeros((z.WxYrs, 12), dtype=int)
        z.WxMonth = np.zeros((z.WxYrs, 12), dtype=object)
        z.WxYear = np.zeros((z.WxYrs, 12))
        z.Temp = np.zeros((z.WxYrs, 12, 31))
        z.Prec = np.zeros((z.WxYrs, 12, 31))

        for year in range(z.WxYrs):
            for month in range(12):
                z.DaysMonth[year][month] = self.next(int)  # Days
                z.WxMonth[year][month] = self.next(str)  # Month (Jan-Dec)
                z.WxYear[year][month] = self.next(int)  # Year
                self.next(EOL)

                for day in range(z.DaysMonth[year][month]):
                    z.Temp[year][month][day] = self.next(float)  # Average Temperature (C)
                    z.Prec[year][month][day] = self.next(float)  # Precipitation (cm)
                    self.next(EOL)

        # Line Beginning After Weather: (Urban Area data)
        z.NumUAs = self.next(int)  # Number of Urban Areas
        z.UABasinArea = self.next(float)  # Urban Area Basin Area (Ha)
        self.next(EOL)

        z.UAId = np.zeros(z.NumUAs)
        z.UAName = np.zeros(z.NumUAs, dtype=object)
        z.UAArea = np.zeros(z.NumUAs)
        z.UAfa = np.zeros(z.NumUAs, dtype=object)
        z.UAfaAreaFrac = np.zeros(z.NumUAs)
        z.UATD = np.zeros(z.NumUAs, dtype=object)
        z.UATDAreaFrac = np.zeros(z.NumUAs)
        z.UASB = np.zeros(z.NumUAs, dtype=object)
        z.UASBAreaFrac = np.zeros(z.NumUAs)
        z.UAGW = np.zeros(z.NumUAs, dtype=object)
        z.UAGWAreaFrac = np.zeros(z.NumUAs)
        z.UAPS = np.zeros(z.NumUAs, dtype=object)
        z.UAPSAreaFrac = np.zeros(z.NumUAs)
        z.UASS = np.zeros(z.NumUAs, dtype=object)
        z.UASSAreaFrac = np.zeros(z.NumUAs)

        # +1 for "Water"
        z.UALU = np.zeros((z.NumUAs, z.NLU + 1), dtype=object)
        z.UALUArea = np.zeros((z.NumUAs, z.NLU + 1))

        # Lines if Number of Urban Areas > 0: (for each Urban Area)
        for i in range(z.NumUAs):
            # Line 1:
            z.UAId[i] = self.next(int)  # Urban Area ID
            z.UAName[i] = self.next(str)  # Urban Area Name
            z.UAArea[i] = self.next(float)  # Urban Area Area (Ha)
            self.next(EOL)

            # Lines 2 - 17: (For each Land Use Category)
            # +1 for "Water"
            for l in range(z.NLU + 1):
                z.UALU[i][l] = self.next(LandUse.parse)  # Land Use Category
                z.UALUArea[i][l] = self.next(float)  # Urban Land Use Area (Ha)
                self.next(EOL)

            # Line 18:
            z.UAfa[i] = self.next('Farm Animals')
            z.UAfaAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

            # Line 19:
            z.UATD[i] = self.next('Tile Drainage')
            z.UATDAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

            # Line 20:
            z.UASB[i] = self.next('Stream Bank')
            z.UASBAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

            # Line 21:
            z.UAGW[i] = self.next('Groundwater')
            z.UAGWAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

            # Line 22:
            z.UAPS[i] = self.next('Point Sources')
            z.UAPSAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

            # Line 23:
            z.UASS[i] = self.next('Septic Systems')
            z.UASSAreaFrac[i] = self.next(float)  # Area Fraction
            self.next(EOL)

        return z

    def next(self, typ):
        """
        Pop the next token and cast it using the given callable function
        or type. If a scalar value is passed instead, assert that the
        next token value matches and raise a ValueError if it does not.
        """
        value, line_no, col_no = self.fp.next()

        if callable(typ):
            try:
                return typ(value)
            except ValueError:
                log.error('Unexpected token at Line {} Column {}'.format(line_no, col_no))
                raise

        if typ != value:
            raise ValueError('Expected "{}" but got "{}" at Line {} Column {}'.format(typ, value, line_no, col_no))

        return value

    def version_match(self, TranVersionNo, VersionPatternRegex):
        pattern = '^{}$'.format(VersionPatternRegex)
        return re.match(pattern, TranVersionNo)


class GmsWriter(object):
    ENUMS = (YesOrNo, ETflag, GrowFlag, SweepType, LandUse)

    def __init__(self, fp):
        self.fp = csv.writer(fp)

    def write(self, z):
        self.writerow([
            z.NRur,
            z.NUrb,
            z.BasinId,
        ])

        self.writerow([
            z.TranVersionNo,
            z.RecessionCoef,
            z.SeepCoef,
            z.UnsatStor,
            z.SatStor,
            z.InitSnow,
            z.SedDelivRatio_0,
            z.MaxWaterCap,
            z.StreamLength,
            z.AgLength,
            z.UrbLength,
            z.AgSlope3,
            z.AgSlope3to8,
            z.AvSlope,
            z.AEU,
            z.WxYrs,
            z.WxYrBeg,
            z.WxYrEnd,
            # z.SedAFactor,
            z.SedAFactor_0,
            z.TotArea,
            z.TileDrainRatio,
            z.TileDrainDensity,
            z.ETFlag,
            z.AvKF,
        ])

        for i in range(5):
            self.writerow([z.AntMoist[i]])

        for i in range(12):
            self.writerow([
                z.Month[i],
                z.KV[i],
                z.DayHrs[i],
                z.Grow_0[i],
                z.Acoef[i],
                z.StreamWithdrawal[i],
                z.GroundWithdrawal[i],
                z.PcntET[i],
            ])

        for i in range(z.NRur):
            self.writerow([
                z.Landuse[i],
                z.Area[i],
                z.CN[i],
                z.KF[i],
                z.LS[i],
                z.C[i],
                z.P[i],
            ])

        for i in range(z.NRur, z.NLU):
            self.writerow([
                z.Landuse[i],
                z.Area[i],
                z.Imper[i],
                z.CNI[1][i],
                z.CNP[1][i],
                z.TotSusSolids[i],
            ])

        self.writerow([
            YesOrNo.intval(z.PhysFlag),
            YesOrNo.intval(z.PointFlag),
            YesOrNo.intval(z.SeptSysFlag),
            YesOrNo.intval(z.CountyFlag),
            YesOrNo.intval(z.SoilPFlag),
            YesOrNo.intval(z.GWNFlag),
            z.SedAAdjust,
        ])

        self.writerow([
            z.SedNitr,
            z.SedPhos,
            z.GrNitrConc,
            z.GrPhosConc,
            z.BankNFrac,
            z.BankPFrac,
        ])

        # Convert 0-based indexes to 1-based.
        self.writerow([
            z.ManuredAreas,
            z.FirstManureMonth + 1,
            z.LastManureMonth + 1,
            z.FirstManureMonth2 + 1,
            z.LastManureMonth2 + 1,
        ])

        for i in range(z.NRur):
            self.writerow([
                z.NitrConc[i],
                z.PhosConc[i],
            ])

        self.writerow([z.Nqual])

        for i in range(z.Nqual):
            self.writerow([z.Contaminant[i]])

        for u in range(z.NRur, z.NLU):
            for q in range(z.Nqual):
                self.writerow([
                    z.LoadRateImp[u][q],
                    z.LoadRatePerv[u][q],
                    z.DisFract[u][q],
                    z.UrbBMPRed[u][q],
                ])

        for i in range(z.ManuredAreas):
            self.writerow([z.ManNitr[i], z.ManPhos[i]])

        for i in range(12):
            self.writerow([
                z.PointNitr[i],
                z.PointPhos[i],
                z.PointFlow[i],
            ])

        self.writerow([YesOrNo.intval(z.SepticFlag)])

        for i in range(12):
            self.writerow([
                z.NumNormalSys[i],
                z.NumPondSys[i],
                z.NumShortSys[i],
                z.NumDischargeSys[i],
                z.NumSewerSys[i],
            ])

        self.writerow([
            z.NitrSepticLoad,
            z.PhosSepticLoad,
            z.NitrPlantUptake,
            z.PhosPlantUptake,
        ])

        self.writerow([
            z.TileNconc,
            z.TilePConc,
            z.TileSedConc,
        ])

        self.writerow([
            z.InName,
            z.UnitsFileFlag,
            z.AssessDate,
            z.VersionNo,
        ])

        self.writerow([z.ProjName])

        self.writerow([
            z.n1,
            z.n2,
            z.n2b,
            z.n2c,
            z.n2d,
            z.n3,
            z.n4,
        ])

        self.writerow([
            z.n5,
            z.n6,
            z.n6b,
            z.n6c,
            z.n6d,
            z.n7,
            z.n7b,
            z.n8,
            z.n9,
            z.n10,
            z.n11,
        ])

        self.writerow([
            z.n12,
            z.n13,
            z.n13b,
            z.n13c,
            z.n13d,
            z.n14,
            z.n14b,
            z.n15,
            z.n16,
            z.n17,
            z.n18,
        ])

        self.writerow([
            z.n19,
            z.n20,
            z.n21,
            z.n22,
        ])

        self.writerow([
            z.n23,
            z.n23b,
            z.n23c,
            z.n24,
            z.n24b,
            z.n24c,
            z.n24d,
            z.n24e,
        ])

        self.writerow([
            z.n25,
            z.n25b,
            z.n25c,
            z.n25d,
            z.n25e,
            z.n26,
            z.n26b,
            z.n26c,
            z.n27,
            z.n27b,
            z.n28,
            z.n28b,
            z.n29,
        ])

        self.writerow([
            z.n30,
            z.n30b,
            z.n30c,
            z.n30d,
            z.n30e,
            z.n31,
            z.n31b,
            z.n31c,
            z.n32,
            z.n32b,
            z.n32c,
            z.n32d,
            z.n33,
            z.n33b,
            z.n33c,
            z.n33d,
        ])

        self.writerow([
            z.n34,
            z.n35,
            z.n35b,
            z.n36,
            z.n37,
            z.n38,
            z.n38b,
            z.n39,
            z.n40,
        ])

        self.writerow([
            z.n41,
            z.n41b,
            z.n41c,
            z.n41d,
            z.n41e,
            z.n41f,
            z.n41g,
            z.n41h,
            z.n41i,
            z.n41j,
            z.n41k,
            z.n41l,
            z.n42,
            z.n42b,
            z.n42c,
            z.n43,
            z.GRLBN,
            z.NGLBN,
            z.GRLBP,
            z.NGLBP,
            z.NGLManP,
            z.NGLBFC,
            z.GRLBFC,
            z.GRSFC,
            z.GRSN,
            z.GRSP,
        ])

        self.writerow([
            z.n43b,
            z.n43c,
            z.n43d,
            z.n43e,
            z.n43f,
            z.n43g,
            z.n43h,
            z.n43i,
            z.n43j,
            z.n44,
            z.n44b,
            z.n45,
            z.n45b,
            z.n45c,
            z.n45d,
            z.n45e,
            z.n45f,
        ])

        self.writerow([
            z.n46,
            z.n46b,
            z.n46c,
            z.n46d,
            z.n46e,
            z.n46f,
            z.n46g,
            z.n46h,
            z.n46i,
            z.n46j,
            z.n46k,
            z.n46l,
            z.n46m,
            z.n46n,
            z.n46o,
            z.n46p,
        ])

        self.writerow([
            z.n47,
            z.n48,
            z.n49,
            z.n50,
            z.n51,
            z.n52,
            z.n53,
            z.n54,
            z.n55,
            z.n56,
            z.n57,
            z.n58,
            z.n59,
            z.n60,
            z.n61,
            z.n62,
        ])

        self.writerow([
            z.n63,
            z.n64,
            z.n65,
            z.n66,
            z.n66b,
            z.n67,
            z.n68,
            z.n68b,
            z.n69,
            z.n69b,
            z.n69c,
            z.n70,
            z.n70b,
        ])

        self.writerow([
            z.n71,
            z.n71b,
            z.n72,
            z.n73,
            z.n74,
            z.n74b,
            z.n75,
            z.n76,
            z.n76b,
            z.n77,
            z.n77b,
            z.n77c,
            z.n78,
            z.n78b,
        ])

        self.writerow([
            z.n79,
            z.n79b,
            z.n79c,
            z.n80,
            z.n81,
            z.n82,
            z.n82b,
            z.n83,
            z.n84,
            z.n84b,
            z.n85,
            z.n85b,
            z.n85c,
            z.n85d,
            z.n85e,
            z.n85f,
            z.n85g,
        ])

        self.writerow([
            z.n85h,
            z.n85i,
            z.n85j,
            z.n85k,
            z.n85l,
            z.n85m,
            z.n85n,
            z.n85o,
            z.n85p,
            z.n85q,
            z.n85r,
            z.n85s,
            z.n85t,
            z.n85u,
            z.n85v,
        ])

        self.writerow([
            z.n86,
            z.n87,
            z.n88,
            z.n89,
            z.n90,
            z.n91,
            z.n92,
            z.n93,
            z.n94,
            z.n95,
            z.n95b,
            z.n95c,
            z.n95d,
            z.n95e,
        ])

        self.writerow([
            z.n96,
            z.n97,
            z.n98,
            z.n99,
            z.n99b,
            z.n99c,
            z.n99d,
            z.n99e,
            z.n100,
            z.n101,
            z.n101b,
            z.n101c,
            z.n101d,
            z.n101e,
            z.n102,
            z.n103a,
            z.n103b,
            z.n103c,
            z.n103d,
        ])

        self.writerow([
            z.n104,
            z.n105,
            z.n106,
            z.n106b,
            z.n106c,
            z.n106d,
            z.n107,
            z.n107b,
            z.n107c,
            z.n107d,
            z.n107e,
            z.Storm,
            z.CSNAreaSim,
            z.CSNDevType,
        ])

        self.writerow([
            z.Qretention,
            z.FilterWidth,
            z.Capacity,
            z.BasinDeadStorage,
            z.BasinArea,
            z.DaysToDrain,
            z.CleanMon,
            z.PctAreaInfil,
            z.PctStrmBuf,
            z.UrbBankStab,
            z.ISRR[0],
            z.ISRA[0],
            z.ISRR[1],
            z.ISRA[1],
            z.ISRR[2],
            z.ISRA[2],
            z.ISRR[3],
            z.ISRA[3],
            z.ISRR[4],
            z.ISRA[4],
            z.ISRR[5],
            z.ISRA[5],
            z.SweepType,
            z.UrbSweepFrac,
        ])

        for i in range(12):
            self.writerow([z.StreetSweepNo[i]])

        self.writerow([z.OutName])

        self.writerow([
            z.n108,
            z.n109,
            z.n110,
        ])

        self.writerow([
            z.n111,
            z.n111b,
            z.n111c,
            z.n111d,
            z.n112,
            z.n112b,
            z.n112c,
            z.n112d,
            z.n113,
            z.n113b,
            z.n113c,
            z.n113d,
        ])

        self.writerow([
            z.n114,
            z.n115,
            z.n115b,
            z.n116,
            z.n116b,
        ])

        self.writerow([
            z.n117,
            z.n118,
            z.n119,
        ])

        self.writerow([
            z.n120,
            z.n121,
        ])

        self.writerow([
            z.n122,
            z.n123,
        ])

        self.writerow([
            z.n124,
            z.n125,
        ])

        self.writerow([
            z.n126,
            z.n127,
            z.n128,
        ])

        self.writerow([
            z.n129,
            z.n130,
            z.n131,
        ])

        self.writerow([
            z.n132,
            z.n133,
            z.n134,
            z.n135,
            z.n136,
            z.n137,
            z.n138,
            z.n139,
            z.n140,
        ])

        self.writerow([
            z.n141,
            z.n142,
            z.n143,
            z.n144,
            z.n145,
            z.n146,
            z.n147,
            z.n148,
            z.n149,
            z.n150,
            z.n151,
        ])

        self.writerow([
            z.InitNgN,
            z.InitNgP,
            z.InitNgFC,
            z.NGAppSum,
            z.NGBarnSum,
            z.NGTotSum,
            z.InitGrN,
            z.InitGrP,
            z.InitGrFC,
            z.GRAppSum,
            z.GRBarnSum,
            z.GRTotSum,
            YesOrNo.intval(z.AnimalFlag),
        ])

        self.writerow([
            z.WildOrgsDay,
            z.WildDensity,
            z.WuDieoff,
            z.UrbEMC,
            z.SepticOrgsDay,
            z.SepticFailure,
            z.WWTPConc,
            z.InstreamDieoff,
            z.AWMSGrPct,
            z.AWMSNgPct,
            z.RunContPct,
            z.PhytasePct,
        ])

        for i in range(z.NAnimals):
            self.writerow([
                z.AnimalName[i],
                z.NumAnimals[i],
                z.GrazingAnimal_0[i],
                z.AvgAnimalWt[i],
                z.AnimalDailyN[i],
                z.AnimalDailyP[i],
                z.FCOrgsPerDay[i],
            ])

        for i in range(12):
            self.writerow([
                z.Month[i],
                z.NGPctManApp[i],
                z.NGAppNRate[i],
                z.NGAppPRate[i],
                z.NGAppFCRate[i],
                z.NGPctSoilIncRate[i],
                z.NGBarnNRate[i],
                z.NGBarnPRate[i],
                z.NGBarnFCRate[i],
            ])

        for i in range(12):
            self.writerow([
                z.Month[i],
                z.PctGrazing[i],
                z.PctStreams[i],
                z.GrazingNRate[i],
                z.GrazingPRate[i],
                z.GrazingFCRate[i],
                z.GRPctManApp[i],
                z.GRAppNRate[i],
                z.GRAppPRate[i],
                z.GRAppFCRate[i],
                z.GRPctSoilIncRate[i],
                z.GRBarnNRate[i],
                z.GRBarnPRate[i],
                z.GRBarnFCRate[i],
            ])

        self.writerow([
            z.ShedAreaDrainLake,
            z.RetentNLake,
            z.RetentPLake,
            z.RetentSedLake,
            z.AttenFlowDist,
            z.AttenFlowVel,
            z.AttenLossRateN,
            z.AttenLossRateP,
            z.AttenLossRateTSS,
            z.AttenLossRatePath,
            z.StreamFlowVolAdj,
        ])

        for year in range(z.WxYrs):
            for month in range(12):
                self.writerow([
                    z.DaysMonth[year][month],
                    z.WxMonth[year][month],
                    z.WxYear[year][month],
                ])
                for day in range(z.DaysMonth[year][month]):
                    self.writerow([
                        z.Temp[year][month][day],
                        z.Prec[year][month][day],
                    ])

        self.writerow([
            z.NumUAs,
            z.UABasinArea,
        ])

        for i in range(z.NumUAs):
            self.writerow([
                z.UAId[i],
                z.UAName[i],
                z.UAArea[i],
            ])

            # +1 for "Water"
            for l in range(z.NLU + 1):
                self.writerow([
                    z.UALU[i][l],
                    z.UALUArea[i][l],
                ])

            self.writerow([
                z.UAfa[i],
                z.UAfaAreaFrac[i],
            ])

            self.writerow([
                z.UATD[i],
                z.UATDAreaFrac[i],
            ])

            self.writerow([
                z.UASB[i],
                z.UASBAreaFrac[i],
            ])

            self.writerow([
                z.UAGW[i],
                z.UAGWAreaFrac[i],
            ])

            self.writerow([
                z.UAPS[i],
                z.UAPSAreaFrac[i],
            ])

            self.writerow([
                z.UASS[i],
                z.UASSAreaFrac[i],
            ])

    def writerow(self, row):
        self.fp.writerow([self.serialize_value(col) for col in row])

    def serialize_value(self, value):
        if isinstance(value, basestring):
            return self.serialize_enum(value)
        return value

    def serialize_enum(self, value):
        # Find the first valid enum that can parse this value.
        for enm in self.ENUMS:
            try:
                return enm.gmsval(value)
            except ValueError:
                pass
        return value



def PcntUrbanArea(NRur, NUrb, Area):
    result = 0
    areatotal = AreaTotal(NRur, NUrb, Area)
    urbareatotal = UrbAreaTotal(NRur, NUrb, Area)
    if areatotal == 0:
        result = 0
    else:
        result += urbareatotal / areatotal
    return result


def PcntUrbanArea_2(NRur, NUrb, Area):
    areatotal = AreaTotal_2(Area)
    if areatotal != 0:
        return UrbAreaTotal_2(NRur, NUrb, Area) / areatotal
    else:
        return 0


def PConc(NRur, NUrb, PhosConc, ManPhos, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
          LastManureMonth2):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((12, nlu))
    for i in range(12):
        for l in range(NRur):
            result[i][l] = PhosConc[l]
            # MANURE SPREADING DAYS FOR FIRST SPREADING PERIOD
            if l < ManuredAreas and i >= FirstManureMonth and i <= LastManureMonth:
                result[i][l] = ManPhos[l]
            # MANURE SPREADING DAYS FOR SECOND SPREADING PERIOD
            if l < ManuredAreas and i >= FirstManureMonth2 and i <= LastManureMonth2:
                result[i][l] = ManPhos[l]
    return result

def PConc_2(NRur, NUrb, PhosConc, ManPhos, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
          LastManureMonth2):
    if(FirstManureMonth < 0 and FirstManureMonth2 < 0 and LastManureMonth < 0 and LastManureMonth2 < 0):
        return np.reshape(np.repeat(PhosConc[None,:], repeats=12, axis=0), (12, -1))
    else:
        nlu = NLU_function(NRur, NUrb)
        result = np.reshape(np.repeat(PhosConc, repeats=12, axis=0), (12, nlu))
        result[FirstManureMonth:LastManureMonth, :ManuredAreas] = ManPhos
        result[FirstManureMonth2:LastManureMonth2, :ManuredAreas] = ManPhos
        return result

try:
    from Percolation_inner_compiled import Percolation_inner
except ImportError:
    print("Unable to import compiled Percolation_inner, using slower version")
    from Percolation_inner import Percolation_inner


@memoize
def Percolation(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    result = np.zeros((NYrs, 12, 31))
    percolation = np.zeros((NYrs, 12, 31))
    infiltration = Infiltration(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper,
                                ISRR, ISRA, CN)
    unsatstor_carryover = UnsatStor_0
    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = unsatstor_carryover
                result[Y][i][j] = result[Y][i][j] + infiltration[Y][i][j]
                if et[Y][i][j] >= result[Y][i][j]:
                    result[Y][i][j] = 0
                else:
                    result[Y][i][j] = result[Y][i][j] - et[Y][i][j]
                if result[Y][i][j] > MaxWaterCap:
                    percolation[Y][i][j] = result[Y][i][j] - MaxWaterCap
                    result[Y][i][j] = MaxWaterCap
                else:
                    pass
                unsatstor_carryover = result[Y][i][j]
    return percolation


def Percolation_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    infiltration = Infiltration_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN)

    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    return Percolation_inner(NYrs, UnsatStor_0, DaysMonth, MaxWaterCap, infiltration, et)

    #   NYrs = arg(0, name=NYrs)  :: int64
    #   UnsatStor_0 = arg(1, name=UnsatStor_0)  :: float64
    #   DaysMonth = arg(2, name=DaysMonth)  :: array(int32, 2d, C)
    #   MaxWaterCap = arg(3, name=MaxWaterCap)  :: float64
    #   infiltration = arg(4, name=infiltration)  :: array(float64, 3d, C)
    #   et = arg(5, name=et)  :: array(float64, 3d, C)

# -*- coding: utf-8 -*-

"""
Imported from PrelimCalculations.bas
"""


log = logging.getLogger(__name__)


def InitialCalculations(z):
    # OBTAIN THE LENGTH OF STREAMS IN AGRICULTURAL AREAS
    # z.AGSTRM = z.AgLength / z.StreamLength if z.StreamLength > 0 else 0

    # Obtain areas in Ha for Urban, Agricultural and Forested landuse
    for l in range(z.NRur):
        if z.Landuse[l] is LandUse.FOREST:
            z.ForestAreaTotal += z.Area[l]
        # elif z.Landuse[l] is LandUse.CROPLAND:
        #     z.AgAreaTotal += z.Area[l]
        # elif z.Landuse[l] is LandUse.HAY_PAST:
        #     z.AgAreaTotal += z.Area[l]
        # elif z.Landuse[l] is LandUse.TURFGRASS:
        #     z.AgAreaTotal += z.Area[l]

        # z.NewCN[0][l] = z.CN[l] / (2.334 - 0.01334 * z.CN[l])
        # z.NewCN[2][l] = z.CN[l] / (0.4036 + 0.0059 * z.CN[l])
        # if z.NewCN[2][l] > 100:
        #     z.NewCN[2][l] = 100

    # for l in range(z.NRur, z.NLU):
    # z.CNI[0][l] = z.CNI[1][l] / (2.334 - 0.01334 * z.CNI[1][1])
    # z.CNI[2][l] = z.CNI[1][l] / (0.4036 + 0.0059 * z.CNI[1][l])
    #
    # print(z.CNI_2[0][l],z.CNI[0][l])
    # print(z.CNI_2[1][l],z.CNI[1][l])
    # print(z.CNI_2[2][l],z.CNI[2][l])
    # z.CNP[0][l] = z.CNP[1][l] / (2.334 - 0.01334 * z.CNP[1][1])
    # z.CNP[2][l] = z.CNP[1][l] / (0.4036 + 0.0059 * z.CNP[1][l])

    # if z.FilterWidth <= 30:
    #     z.FilterEff = z.FilterWidth / 30
    # else:
    #     z.FilterEff = 1

    # TODO: BasinArea is never supposed to be over 0, this retention basin data set DNE according to Barry
    # Model and Tests complete with no errors without this section of code
    # if z.BasinArea > 0:
    #     z.BasinVol = z.BasinDeadStorage
    #     z.Difference = z.Capacity - z.BasinDeadStorage
    #     z.OutletCoef = 0
    #
    #     while z.Difference > 0:
    #         z.OutletCoef += 0.001
    #         z.Volume = z.Capacity - z.BasinDeadStorage
    #         for k in range(z.DaysToDrain):
    #             z.Head = z.Volume / z.BasinArea
    #             if z.Volume > 0:
    #                 z.Flow = 382700 * z.OutletCoef * math.sqrt(z.Head)
    #             else:
    #                 z.Flow = 0
    #             z.Volume -= z.Flow
    #         z.Difference = z.Volume
    #
    #     z.OutletCoef -= 0.001
    #     z.Difference = z.Capacity - z.BasinDeadStorage
    #
    #     while z.Difference > 0:
    #         z.OutletCoef += 0.0001
    #         z.Volume = z.Capacity - z.BasinDeadStorage
    #         for k in range(z.DaysToDrain):
    #             z.Head = z.Volume / z.BasinArea
    #             z.Flow = 382700 * z.OutletCoef * math.sqrt(z.Head)
    #             z.Volume -= z.Flow
    #         z.Difference = z.Volume

    # ANTECEDANT MOISTURE OUT TO 5 DAYS
    z.AMC5_2 = 0
    for k in range(5):
        z.AMC5_2 += z.AntMoist[k]

# -*- coding: utf-8 -*-



log = logging.getLogger(__name__)


def ReDimRunQualVars():
    pass



@memoize
def pRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc, ManuredAreas,
            FirstManureMonth, LastManureMonth, ManPhos, FirstManureMonth2,
            LastManureMonth2):
    result = np.zeros((NYrs, 12))
    rur_q_runoff = RurQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0)
    p_conc = PConc(NRur, NUrb, PhosConc, ManPhos, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
                   LastManureMonth2)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(NRur):
                result[Y][i] += 0.1 * p_conc[i][l] * rur_q_runoff[Y][l][i] * Area[l]
    return result


@memoize
def pRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, PhosConc, ManuredAreas,
              FirstManureMonth, LastManureMonth, ManPhos, FirstManureMonth2, LastManureMonth2):
    p_conc = PConc_2(NRur, NUrb, PhosConc, ManPhos, ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2,
                   LastManureMonth2)[:, :NRur]
    rur_q_runoff = RurQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0)
    return 0.1 * np.sum(p_conc * rur_q_runoff * Area[:NRur], axis=2)



@memoize
def Qrun(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    retention = Retention(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        result[Y][i][j][l] = 0
                        if CN[l] > 0:
                            if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                                result[Y][i][j][l] = (water[Y][i][j] - 0.2 * retention[Y][i][j][l]) ** 2 / (
                                        water[Y][i][j] + 0.8 * retention[Y][i][j][l])
    return result


@memoize
def Qrun_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], nlu, axis=3)
    TempE = np.repeat(Temp[:, :, :, None], nlu, axis=3)
    cnrur = np.tile(CN[None, None, None, :], (NYrs, 12, 31, 1))
    retention = Retention_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)
    retention02 = 0.2 * retention
    # val = np.zeros((NYrs, 12, 31, nlu))
    nonzero = np.where((TempE > 0) & (water > 0.01) & (water >= retention02) & (cnrur > 0))
    result[nonzero] = (water[nonzero] - retention02[nonzero]) ** 2 / (water[nonzero] + 0.8 * retention[nonzero])
    return result



@memoize
def QrunI(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0):
    result = np.zeros((NYrs, 12, 31, 16))  # TODO: should this be nlu?
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    cni = CNI(NRur, NUrb, CNI_0)
    c_num_imperv_reten = CNumImpervReten(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNI_0, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur, nlu):  # TODO: what is this for?
                        result[Y][i][j][l] = 0
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cni[1][l] > 0:
                                if water[Y][i][j] >= 0.2 * c_num_imperv_reten[Y][i][j][l]:
                                    result[Y][i][j][l] = (water[Y][i][j] - 0.2 * c_num_imperv_reten[Y][i][j][
                                        l]) ** 2 / (
                                                                 water[Y][i][j] + 0.8 * c_num_imperv_reten[Y][i][j][l])
    return result


@memoize
def QrunI_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], nlu, axis=3)
    TempE = np.repeat(Temp[:, :, :, None], nlu, axis=3)
    cni = CNI_2(NRur, NUrb, CNI_0)
    cni_1 = np.tile(cni[1][None, None, None, :], (NYrs, 12, 31, 1))
    c_num_imperv_reten = CNumImpervReten_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNI_0,
                                           Grow_0)
    c_num_imperv_reten02 = 0.2 * c_num_imperv_reten
    nonzero = np.where((TempE > 0) & (water >= 0.05) & (cni_1 > 0) & (water >= c_num_imperv_reten02))
    result[nonzero] = (water[nonzero] - c_num_imperv_reten02[nonzero]) ** 2 / (
            water[nonzero] + 0.8 * c_num_imperv_reten[nonzero])
    return result



@memoize
def QrunP(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0):
    result = np.zeros((NYrs, 12, 31, 16))  # TODO: should this be nlu?
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    cnp = CNP(NRur, NUrb, CNP_0)
    c_num_perv_reten = CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNP_0, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur, nlu):  # TODO: what is this for?
                        result[Y][i][j][l] = 0
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if cnp[1][l] > 0:
                                if water[Y][i][j] >= 0.2 * c_num_perv_reten[Y][i][j][l]:
                                    result[Y][i][j][l] = (water[Y][i][j] - 0.2 * c_num_perv_reten[Y][i][j][l]) ** 2 / (
                                            water[Y][i][j] + 0.8 * c_num_perv_reten[Y][i][j][l])
    return result


@memoize
def QrunP_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:, :, :, None], nlu, axis=3)
    TempE = np.repeat(Temp[:, :, :, None], nlu, axis=3)
    c_num_perv_reten = CNumPervReten_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CNP_0, Grow_0)
    c_num_perv_reten02 = 0.2 * c_num_perv_reten
    cnp = CNP_2(NRur, NUrb, CNP_0)
    cnp_1 = np.tile(cnp[1][None, None, None, :], (NYrs, 12, 31, 1))
    nonzero = np.where((TempE > 0) & (water >= 0.05) & (cnp_1 > 0) & (water >= c_num_perv_reten02))
    result[nonzero] = (water[nonzero] - c_num_perv_reten02[nonzero]) ** 2 / (
            water[nonzero] + 0.8 * c_num_perv_reten[nonzero])
    return result



@memoize
def QTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, CN):
    result = np.zeros((NYrs, 12, 31))
    urban_q_total_1 = UrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                    Grow_0, CNP_0, Imper, ISRR, ISRA)
    rural_q_total = RuralQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                # z.QTotal = 0
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i][j] = urban_q_total_1[Y][i][j] + rural_q_total[Y][i][j]
    return result


@memoize
def QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, CN):
    result = np.zeros((NYrs, 12, 31))
    urban_q_total_1 = UrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                      Grow_0, CNP_0, Imper, ISRR, ISRA)
    rural_q_total = RuralQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result[np.where((Temp > 0) & (water > 0))] = urban_q_total_1[np.where((Temp > 0) & (water > 0))] + rural_q_total[
        np.where((Temp > 0) & (water > 0))]

    return result



def Rain_inner(NYrs, DaysMonth, Temp, Prec):
    result = np.zeros((NYrs, 12, 31))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = 0
                if Temp[Y][i][j] <= 0:
                    pass
                else:
                    result[Y][i][j] = Prec[Y][i][j]
    return result

@memoize
def Rain(NYrs, DaysMonth, Temp, Prec):
    return Rain_inner(NYrs,DaysMonth,Temp,Prec)

# @time_function
# @jit(cache=True, nopython = True)
def Rain_2(Temp, Prec):
    return np.where(Temp <= 0,0,Prec )
# -*- coding: utf-8 -*-

"""
Initialize variables and perfom some preliminary calculations.

Imported from ReadAllDataFiles.bas
"""


log = logging.getLogger(__name__)



def ReadAllData(z):
    z.GrazingN = GrazingN_2(z.PctGrazing, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN)
    # z.GRInitBarnN = GRInitBarnN.GRInitBarnN(z.InitGrN, z.GRPctManApp, z.PctGrazing)
    z.GRStreamN = GRStreamN_2(z.PctStreams, z.PctGrazing, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt,
                              z.AnimalDailyN)
    z.GRAccManAppN = GRAccManAppN_2(z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN, z.GRPctManApp,
                                    z.PctGrazing)
    z.NGAppManN = NGAppManN_2(z.NGPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN)
    z.NGLostBarnN = NGLostBarnN_2(z.NYrs, z.NGPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN,
                                  z.NGBarnNRate, z.Prec,
                                  z.DaysMonth, z.AWMSNgPct, z.NgAWMSCoeffN, z.RunContPct, z.RunConCoeffN)

    z.GRLostBarnN = GRLostBarnN_2(z.NYrs, z.Prec, z.DaysMonth, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt,
                                  z.AnimalDailyN, z.GRPctManApp, z.PctGrazing, z.GRBarnNRate, z.AWMSGrPct,
                                  z.GrAWMSCoeffN, z.RunContPct, z.RunConCoeffN)

    z.GRLostManN = GRLostManN_2(z.NYrs, z.GRPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN,
                                z.GRAppNRate,
                                z.Prec, z.DaysMonth, z.GRPctSoilIncRate)

    z.NGLostManN = NGLostManN_2(z.NYrs, z.NGPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN,
                                z.NGAppNRate,
                                z.Prec, z.DaysMonth, z.NGPctSoilIncRate)

    z.GRLossN = GRLossN_2(z.NYrs, z.PctStreams, z.PctGrazing, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt,
                          z.AnimalDailyN,
                          z.GrazingNRate, z.Prec, z.DaysMonth)

    # If RunQual output is requested, then redim RunQual values
    ReDimRunQualVars()

    # Set the Total AEU to the value from the Animal Density layer

    for i in range(12):
        z.AnnDayHrs += z.DayHrs[i]

    if z.SepticFlag is YesOrNo.YES:
        for i in range(12):
            z.SepticsDay[i] = (z.NumNormalSys[i] + z.NumPondSys[i] +
                               z.NumShortSys[i] + z.NumDischargeSys[i])

    for i in range(12):
        if z.SweepType is SweepType.VACUUM:
            if z.StreetSweepNo[i] == 0:
                z.SweepFrac[i] = 1
            if z.StreetSweepNo[i] == 1:
                z.SweepFrac[i] = 0.94
            if z.StreetSweepNo[i] == 2:
                z.SweepFrac[i] = 0.89
            if z.StreetSweepNo[i] == 3:
                z.SweepFrac[i] = 0.84
            if z.StreetSweepNo[i] >= 4:
                z.SweepFrac[i] = 0.79
        elif z.SweepType is SweepType.MECHANICAL:
            if z.StreetSweepNo[i] == 0:
                z.SweepFrac[i] = 1
            if z.StreetSweepNo[i] == 1:
                z.SweepFrac[i] = 0.99
            if z.StreetSweepNo[i] == 2:
                z.SweepFrac[i] = 0.98
            if z.StreetSweepNo[i] == 3:
                z.SweepFrac[i] = 0.97
            if z.StreetSweepNo[i] >= 4:
                z.SweepFrac[i] = 0.96
        else:
            raise ValueError('Invalid value for SweepType')

    # Get the Animal values
    # z.InitGrN = 0
    z.InitGrP = 0
    z.InitGrFC = 0
    # z.InitNgN = 0
    z.InitNgP = 0
    z.InitNgFC = 0

    for a in range(9):
        if GrazingAnimal(z.GrazingAnimal_0)[a] is YesOrNo.NO:
            # z.NGLoadN[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.AnimalDailyN[a] * 365
            z.NGLoadP[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.AnimalDailyP[a] * 365
            z.NGLoadFC[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.FCOrgsPerDay[a] * 365
            # z.InitNgN += z.NGLoadN[a]
            z.InitNgP += z.NGLoadP[a]
            z.InitNgFC += z.NGLoadFC[a]
        elif GrazingAnimal(z.GrazingAnimal_0)[a] is YesOrNo.YES:
            # z.GRLoadNStorage[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.AnimalDailyN[a] * 365
            z.GRLoadP[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.AnimalDailyP[a] * 365
            z.GRLoadFC[a] = (z.NumAnimals[a] * z.AvgAnimalWt[a] / 1000) * z.FCOrgsPerDay[a] * 365
            # z.InitGrN += z.GRLoadN[a]
            z.InitGrP += z.GRLoadP[a]
            z.InitGrFC += z.GRLoadFC[a]
        else:
            raise ValueError('Unexpected value for GrazingAnimal')

    # Get the Non-Grazing Animal Worksheet values
    for i in range(12):
        # For Non-Grazing
        # z.NGAccManAppN[i] += (z.InitNgN / 12) - (z.NGPctManApp[i] * z.InitNgN)

        # if z.NGAccManAppN[i] < 0:
        #     z.NGAccManAppN[i] = 0

        z.NGAccManAppP[i] += (z.InitNgP / 12) - (z.NGPctManApp[i] * z.InitNgP)

        if z.NGAccManAppP[i] < 0:
            z.NGAccManAppP[i] = 0

        z.NGAccManAppFC[i] += (z.InitNgFC / 12) - (z.NGPctManApp[i] * z.InitNgFC)

        if z.NGAccManAppFC[i] < 0:
            z.NGAccManAppFC[i] = 0

        # z.NGAppManN[i] = z.NGPctManApp[i] * z.InitNgN
        # z.NGInitBarnN[i] = z.NGAccManAppN[i] - z.NGAppManN[i]
        #
        # if z.NGInitBarnN[i] < 0:
        #     z.NGInitBarnN[i] = 0

        z.NGAppManP[i] = z.NGPctManApp[i] * z.InitNgP
        z.NGInitBarnP[i] = z.NGAccManAppP[i] - z.NGAppManP[i]

        if z.NGInitBarnP[i] < 0:
            z.NGInitBarnP[i] = 0

        z.NGAppManFC[i] = z.NGPctManApp[i] * z.InitNgFC
        z.NGInitBarnFC[i] = z.NGAccManAppFC[i] - z.NGAppManFC[i]

        if z.NGInitBarnFC[i] < 0:
            z.NGInitBarnFC[i] = 0

    # Read the Grazing Animal Worksheet values

    for i in range(12):
        # z.GrazingN[i] = z.PctGrazing[i] * (z.InitGrN / 12)
        z.GrazingP[i] = z.PctGrazing[i] * (z.InitGrP / 12)
        z.GrazingFC[i] = z.PctGrazing[i] * (z.InitGrFC / 12)

        # z.GRStreamN[i] = z.PctStreams[i] * z.GrazingN[i]
        z.GRStreamP[i] = z.PctStreams[i] * z.GrazingP[i]
        z.GRStreamFC[i] = z.PctStreams[i] * z.GrazingFC[i]

        # Get the annual sum for FC
        z.AvGRStreamFC += z.GRStreamFC[i]
        # z.AvGRStreamN += z.GRStreamN[i]
        z.AvGRStreamP += z.GRStreamP[i]

        # print("old",z.GRAccManAppN[i])
        # print((z.GRAccManAppN[i] + (z.InitGrN / 12) - (z.GRPctManApp[i] * z.InitGrN) - z.GrazingN[i]))
        # z.GRAccManAppN[i] = (z.GRAccManAppN[i] + (z.InitGrN / 12)
        #                      - (z.GRPctManApp[i] * z.InitGrN) - z.GrazingN[i])
        # if z.GRAccManAppN[i] < 0:
        #     z.GRAccManAppN[i] = 0

        z.GRAccManAppP[i] = (z.GRAccManAppP[i] + (z.InitGrP / 12)
                             - (z.GRPctManApp[i] * z.InitGrP) - z.GrazingP[i])
        if z.GRAccManAppP[i] < 0:
            z.GRAccManAppP[i] = 0

        z.GRAccManAppFC[i] = (z.GRAccManAppFC[i] + (z.InitGrFC / 12)
                              - (z.GRPctManApp[i] * z.InitGrFC) - z.GrazingFC[i])
        if z.GRAccManAppFC[i] < 0:
            z.GRAccManAppFC[i] = 0

        # z.GRAppManN[i] = z.GRPctManApp[i] * z.InitGrN
        # z.GRInitBarnN[i] = z.GRAccManAppN[i] - z.GRAppManN[i]
        # if z.GRInitBarnN[i] < 0:
        #     z.GRInitBarnN[i] = 0

        z.GRAppManP[i] = z.GRPctManApp[i] * z.InitGrP
        z.GRInitBarnP[i] = z.GRAccManAppP[i] - z.GRAppManP[i]
        if z.GRInitBarnP[i] < 0:
            z.GRInitBarnP[i] = 0

        z.GRAppManFC[i] = z.GRPctManApp[i] * z.InitGrFC
        z.GRInitBarnFC[i] = z.GRAccManAppFC[i] - z.GRAppManFC[i]
        if z.GRInitBarnFC[i] < 0:
            z.GRInitBarnFC[i] = 0

    z.AttenP = FlowDays(z.AttenFlowDist, z.AttenFlowVel) * z.AttenLossRateP
    z.AttenTSS = FlowDays(z.AttenFlowDist, z.AttenFlowVel) * z.AttenLossRateTSS
    z.AttenPath = FlowDays(z.AttenFlowDist, z.AttenFlowVel) * z.AttenLossRatePath

    # Calculate retention coefficients
    z.RetentFactorP = (1 - (z.ShedAreaDrainLake * z.RetentPLake))
    z.RetentFactorSed = (1 - (z.ShedAreaDrainLake * z.RetentSedLake))


@memoize
def RetentFactorN(ShedAreaDrainLake, RetentNLake):
    return (1 - (ShedAreaDrainLake * RetentNLake))

# def RetentFactorN_2():
#     pass



@memoize
def Retention(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu)) # Why nlu ?
    c_num = CNum(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, CN, NRur, NUrb, Grow_0)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        if CN[l] > 0:#TODO:CN is set to zero in datamodel
                            result[Y][i][j][l] = 2540 / c_num[Y][i][j][l] - 25.4
                            if result[Y][i][j][l] < 0:
                                result[Y][i][j][l] = 0
    return result

@memoize
def Retention_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    c_num = CNum_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, CN, NRur, NUrb, Grow_0)
    cnrur = np.tile(CN[:NRur][None, None, None, :], (NYrs, 12, 31, 1))
    water = np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)[:,:,:,None],NRur, axis=3 )
    TempE = np.repeat(Temp[:, :, :, None], NRur, axis=3)
    result[np.where((TempE>0) & (water > 0.01) & (cnrur > 0))] = 2540 / c_num[np.where((TempE>0) & (water > 0.01) & (cnrur>0))] - 25.4
    result[np.where(result<0)] = 0
    return result



# Precipitation.Precipitation(z.NYrs, z.DaysMonth, z.Prec)ize
def RetentionEff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                 Imper, ISRR, ISRA, PctAreaInfil):
    result = 0
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urbanqtotal = UrbanQTotal(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR,
                              ISRA)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        if Qretention > 0:
                            if urbanqtotal[Y][i][j] > 0:
                                if urbanqtotal[Y][i][j] <= Qretention * PctAreaInfil:
                                    result = 1
                                else:
                                    result = Qretention * PctAreaInfil / urbanqtotal[Y][i][j]
                else:
                    pass
    return result


def RetentionEff_3(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                   CNP_0, Imper, ISRR, ISRA, PctAreaInfil):
    result = np.zeros((NYrs, 12, 31))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urbanqtotal = UrbanQTotal_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA)
    result[np.where((Temp > 0) & (water > 0.05) & (Qretention > 0) & (urbanqtotal > 0) & (
                urbanqtotal <= Qretention * PctAreaInfil))] = 1
    result[np.where((Temp > 0) & (water > 0.05) & (Qretention > 0) & (urbanqtotal > 0) & (
                urbanqtotal > Qretention * PctAreaInfil))] = \
        Qretention * PctAreaInfil / urbanqtotal[np.where(
            (Temp > 0) & (water > 0.05) & (Qretention > 0) & (urbanqtotal > 0) & (
                        urbanqtotal > Qretention * PctAreaInfil))]
    np.nonzero(result)
    return

@memoize
def RetentionEff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                   CNP_0, Imper, ISRR, ISRA, PctAreaInfil):
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urbanqtotal = UrbanQTotal_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA)
    try:
        test = urbanqtotal[np.where((Temp > 0) & (water > 0.05) & (Qretention > 0) & (urbanqtotal > 0))][::-1][0]
        if test <= Qretention * PctAreaInfil:
            return 1
        else:
            return Qretention * PctAreaInfil / test
    except IndexError:
        return 0


def Runoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity):
    result = np.zeros((NYrs, 12))
    adj_q_total = AdjQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper,
                            ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    q_total = QTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN)
    tile_drain_ro = TileDrainRO(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse,
                                Area,
                                TileDrainDensity)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if adj_q_total[Y][i][j] > 0:
                    result[Y][i] += adj_q_total[Y][i][j]
                else:
                    result[Y][i] += q_total[Y][i][j]
                    # ADJUST THE SURFACE RUNOFF
            result[Y][i] = result[Y][i] - tile_drain_ro[Y][i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result

@memoize
def Runoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
           ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity):
    adj_q_total = AdjQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper,
                            ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    q_total = QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN)
    tile_drain_ro = TileDrainRO_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse,
                                Area,
                                TileDrainDensity)
    result = np.where(adj_q_total>0,adj_q_total,q_total)
    result = np.sum(result, axis=2) - tile_drain_ro
    result[result<0] = 0
    return result

# @jit(cache=True,nopython=True)
# def Runoff_3(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
#            ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity):
#     result = np.zeros((NYrs, 12))
#     adj_q_total = AdjQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
#                             Imper,
#                             ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
#     q_total = QTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
#                      ISRR, ISRA, CN)
#     tile_drain_ro = TileDrainRO_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse,
#                                 Area,
#                                 TileDrainDensity)
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 if adj_q_total[Y][i][j] > 0:
#                     result[Y][i] += adj_q_total[Y][i][j]
#                 else:
#                     result[Y][i] += q_total[Y][i][j]
#                     # ADJUST THE SURFACE RUNOFF
#             result[Y][i] = result[Y][i] - tile_drain_ro[Y][i]
#             if result[Y][i] < 0:
#                 result[Y][i] = 0
#     return result

# -*- coding: utf-8 -*-



log = logging.getLogger(__name__)


def ReDimRunQualVars():
    pass


# @time_function
@memoize
def RuralQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area):
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    q_run = Qrun(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)
    rur_area_total = RurAreaTotal(NRur, Area)
    retention = Retention(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)
    area_total = AreaTotal(NRur, NUrb, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = 0  # this does not need to be calculated daily
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        if CN[l] > 0:  # TODO: CN in set to all zeros in datamodel:42
                            if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                                result[Y][i][j] += q_run[Y][i][j][l] * Area[l] / rur_area_total
                    if result[Y][i][j] > 0:
                        result[Y][i][j] *= rur_area_total / area_total
                    else:
                        result[Y][i][j] = 0  # TODO: this seems redundant
                else:
                    pass
    return result

@memoize
def RuralQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area):
    result = np.zeros((NYrs, 12, 31))
    q_run = Qrun_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)
    area_total = AreaTotal(NRur, NUrb, Area)
    qrun_area = q_run * Area
    result = np.sum(qrun_area, axis=3)/area_total
    return result


# @memoize
# def RuralRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec,  NRur, CN, NUrb, AntMoist_0, Grow_0, Area):
#     result = np.zeros((NYrs, 12))
#     water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
#     ruralqtotal = RuralQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, NUrb, AntMoist_0, Grow_0, Area)
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
#                     result[Y][i] += ruralqtotal[Y][i][j]
#                 else:
#                     pass
#     return result
#
#
# def RuralRunoff_2():
#     pass



#RurAreaTotal is faster
@memoize
# @time_function
def RurAreaTotal(NRur, Area):
    result = 0
    for l in range(NRur):
        result += Area[l]
    return result

# @memoize
# @time_function
def RurAreaTotal_2(NRur, Area):
    return np.sum(Area[0:NRur])


@memoize
def RurEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area):
    result = np.zeros((NYrs, 12, 31, NRur))
    erosiv = Erosiv(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef)
    water = Water(NYrs,DaysMonth,InitSnow_0,Temp,Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        result[Y][i][j][l] = 1.32 * erosiv[Y][i][j] * KF[l] * LS[l] * C[l] * P[l] * Area[l]
    return result

@memoize
def RurEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area):
    erosiv = np.reshape(np.repeat(Erosiv_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef), NRur, axis=2),(NYrs, 12, 31, NRur))
    water = np.reshape(np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec),NRur,axis=2),(NYrs, 12, 31, NRur)) #TODO: is there a way to repeating
    resized_temp = np.reshape(np.repeat(Temp,NRur,axis=2),(NYrs, 12, 31, NRur))
    temp = KF * LS * C * P * Area
    return np.where((resized_temp > 0) & (water > 0.01), 1.32 * erosiv * temp[:NRur], 0)



@memoize
def RurQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0):
    result = np.zeros((NYrs, 16, 12))
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    retention = Retention(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)
    qrun = Qrun(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(nlu):
                result[Y, l, i] = 0.0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    for l in range(NRur):
                        if CN[l] > 0:
                            if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                                result[Y][l][i] += qrun[Y][i][j][l]
                            else:
                                pass
                        else:
                            pass
                else:
                    pass

    return result

@memoize
def RurQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0):
    water = np.reshape(np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec), repeats=NRur, axis=2),
                       (NYrs, 12, 31, NRur))
    retention = Retention_2(NYrs, DaysMonth, Temp, Prec, InitSnow_0, AntMoist_0, NRur, NUrb, CN, Grow_0)[:, :, :, :NRur]
    qrun = Qrun_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, CN, AntMoist_0, Grow_0)[:, :, :, :NRur]
    return np.sum(np.where((water >= 0.2 * retention) & (CN[:NRur] > 0), qrun, 0), axis=2)



@memoize
def SatStor(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    result = np.zeros((NYrs, 12, 31))
    grflow = np.zeros((NYrs, 12, 31))
    deepseep = np.zeros((NYrs, 12, 31))
    percolation = Percolation(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper,
                              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    satstor_carryover = SatStor_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = satstor_carryover
                grflow[Y][i][j] = RecessionCoef * result[Y][i][j]
                deepseep[Y][i][j] = SeepCoef * result[Y][i][j]
                result[Y][i][j] = result[Y][i][j] + percolation[Y][i][j] - grflow[Y][i][j] - deepseep[Y][i][j]
                if result[Y][i][j] < 0:
                    result[Y][i][j] = 0
                satstor_carryover = result[Y][i][j]
    return result


@memoize
def SatStor_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef):
    percolation = Percolation_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap)
    return DeepSeep_inner(NYrs, SatStor_0, DaysMonth, RecessionCoef, SeepCoef, percolation)[2]



@memoize
def SedAFactor(NumAnimals, AvgAnimalWt, NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area, SedAFactor_0, AvKF, AvSlope,
               SedAAdjust):
    result = SedAFactor_0
    pcnturbanarea = PcntUrbanArea(NRur, NUrb, Area)
    aeu = AEU(NumAnimals, AvgAnimalWt, NRur, NUrb, Area)
    avcn = AvCN(NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area)
    # Recalculate Sed A Factor using updated AEU value based on animal data
    result = ((0.00467 * pcnturbanarea) +
              (0.000863 * aeu) +
              (0.000001 * avcn) +
              (0.000425 * AvKF) +
              (0.000001 * AvSlope) - 0.000036) * SedAAdjust

    if result < 0.00001:
        result = 0.00001
    return result

# @time_function #vectorization wasn't any faster
# def SedAFactor_2(NumAnimals, AvgAnimalWt, NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area, SedAFactor_0, AvKF, AvSlope,
#                SedAAdjust):
#     pcnturbanarea = PcntUrbanArea_2(NRur, NUrb, Area)
#     aeu = AEU_2(NumAnimals, AvgAnimalWt, NRur, NUrb, Area)
#     avcn = AvCN(NRur, NUrb, CNI_0, CNP_0, CN, Imper, Area)
#     return max(((0.00467 * pcnturbanarea) +
#               (0.000863 * aeu) +
#               (0.000001 * avcn) +
#               (0.000425 * AvKF) +
#               (0.000001 * AvSlope) - 0.000036) * SedAAdjust,0.00001)


@memoize
def SedDelivRatio(SedDelivRatio_0):
    if SedDelivRatio_0 == 0:
        result = 0.0001
    else:
        result = SedDelivRatio_0
    return result


# def SedDelivRatio_2():
#     pass



# @memoize
def SEDFEN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
           CNP_0, Imper,
           ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
           RecessionCoef, SeepCoef
           , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
           StreamWithdrawal, GroundWithdrawal
           , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
           SedAAdjust, StreamLength, AgLength, n42, n45, n85):
    result = np.zeros((NYrs, 12))
    streambankeros = StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                    CNP_0, Imper,
                                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                    RecessionCoef, SeepCoef
                                    , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                    StreamWithdrawal, GroundWithdrawal
                                    , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                    SedAAdjust, StreamLength)
    agstrm = AGSTRM(AgLength, StreamLength)
    for Y in range(NYrs):
        for i in range(12):
            if n42 > 0:
                result[Y][i] = (n45 / n42) * streambankeros[Y][i] * agstrm * n85
    return result


def SEDFEN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
             CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
             RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
             StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
             SedAAdjust, StreamLength, AgLength, n42, n45, n85):
    streambankeros = StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                    CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap,
                                    SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                    TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal, NumAnimals,
                                    AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                                    StreamLength)
    agstrm = AGSTRM_2(AgLength, StreamLength)
    if n42 > 0:
        return (n45 / n42) * streambankeros * agstrm * n85
    else:
        return np.zeros((NYrs, 12))



# @memoize
def SEDSTAB(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
            CNP_0, Imper,
            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
            RecessionCoef, SeepCoef
            , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
            StreamWithdrawal, GroundWithdrawal
            , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
            SedAAdjust, StreamLength, n42b, n46c, n85d):
    result = np.zeros((NYrs, 12))
    streambankeros = StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                    CNP_0, Imper,
                                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                    RecessionCoef, SeepCoef
                                    , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                    StreamWithdrawal, GroundWithdrawal
                                    , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                    SedAAdjust, StreamLength)
    for Y in range(NYrs):
        for i in range(12):
            if n42b > 0:
                result[Y][i] = (n46c / n42b) * streambankeros[Y][i] * n85d
    return result


def SEDSTAB_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
              CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
              StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
              AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d):
    streambankeros = StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                      Grow_0,
                                      CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap,
                                      SatStor_0, RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                      TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal, NumAnimals,
                                      AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                                      StreamLength)
    if (n42b > 0):
        return (n46c / n42b) * streambankeros * n85d
    else:
        return np.zeros((NYrs, 12))


@memoize
def SedTrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    result = np.zeros((NYrs, 12))  # These used to be (NYrs,16) but it looks like a mistake
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjqtotal = AdjQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper,
                          ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i] = result[Y][i] + adjqtotal[Y][i][j] ** 1.67
                else:
                    result[Y][i] = result[Y][i]
    return result

@memoize
def SedTrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
               ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN):
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjqtotal = AdjQTotal_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)

    return np.sum(np.where(np.logical_and(Temp > 0, water > 0.01), adjqtotal ** 1.67, 0), axis=2)



# @memoize
def SedYield(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area, NUrb, CNI_0, AntMoist_0, Grow_0,
             ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, CNP_0, Imper, SedDelivRatio_0):
    result = np.zeros((NYrs, 12))
    erosion = Erosion(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    bsed = BSed(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    seddelivratio = SedDelivRatio(SedDelivRatio_0)
    sedtrans = SedTrans(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                        Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    for Y in range(NYrs):
        for i in range(12):
            for m in range(i + 1):
                if bsed[Y][m] > 0:
                    result[Y][i] = result[Y][i] + erosion[Y][m] / bsed[Y][m]
        # for i in range(12):
            result[Y][i] = seddelivratio * sedtrans[Y][i] * result[Y][i]
    return result

@memoize
def SedYield_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area, NUrb, CNI_0, AntMoist_0, Grow_0,
               ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, CNP_0, Imper, SedDelivRatio_0):
    erosion = Erosion_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area)
    bsed = BSed_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)
    seddelivratio = SedDelivRatio(SedDelivRatio_0)
    sedtrans = SedTrans_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN)

    return seddelivratio * sedtrans * np.cumsum(np.where(bsed > 0, erosion / bsed, 0), axis=1)



@memoize
def SedYield_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
               Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
               StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
               AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
               Acoef, KF, LS, C, P, SedDelivRatio_0):
    result = np.zeros((NYrs, 12))
    sedyield = SedYield(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area, NUrb, CNI_0,
                        AntMoist_0, Grow_0,
                        ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, CNP_0, Imper, SedDelivRatio_0)
    streambankeros_2 = StreamBankEros_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs,
                                        MaxWaterCap, SatStor_0,
                                        RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                        TileDrainDensity, PointFlow,
                                        StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj,
                                        SedAFactor_0,
                                        AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45,
                                        n85, UrbBankStab)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = sedyield[Y][i] + streambankeros_2[Y][i] / 1000
    return result

@memoize
def SedYield_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                 Grow_0, CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                 RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                 StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                 AvKF, AvSlope, SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab,
                 Acoef, KF, LS, C, P, SedDelivRatio_0):
    return SedYield_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, Acoef, NRur, KF, LS, C, P, Area, NUrb, CNI_0, AntMoist_0,
                      Grow_0, ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, CNP_0, Imper,
                      SedDelivRatio_0) + StreamBankEros_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                                          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                                          UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                                          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b,
                                                          Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                                                          GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj,
                                                          SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength, n42b,
                                                          n46c, n85d, AgLength, n42, n45, n85, UrbBankStab) / 1000

# -*- coding: utf-8 -*-

"""
Imported from StreamBank.bas
"""


log = logging.getLogger(__name__)


def CalculateStreamBankEros(z, Y):
    # CALCULATE THE STREAM BANK SEDIMENT AND N AND P
    for i in range(12):
        # CALCULATE ER FACTOR FOR STREAMBANK EROSION
        # z.LE[Y][i] = z.SedAFactor * (z.StreamFlowVolAdj * (z.StreamFlowVol[Y][i] ** 0.6))

        # z.StreamBankEros[Y][i] = z.LE[Y][i] * z.StreamLength * 1500 * 1.5

        # print("StreamBankEros orig = ", z.StreamBankEros[Y][i], "StreamBankEros new = ", z.StreamBankEros_temp[Y][i])
        # print(z.StreamBankEros[Y][i] == z.StreamBankEros_temp[Y][i])

        # CALCULATE STREAM ABANK N AND P
        # z.StreamBankN[Y][i] = \
        #     StreamBankEros_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
        #                      z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
        #                      z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
        #                      z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
        #                      z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
        #                      z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
        #                      z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength,
        #                      z.n42, z.n54, z.n85, z.UrbBankStab)[Y][i] * (z.SedNitr / 1000000) * z.BankNFrac
        z.StreamBankP[Y][i] = \
            StreamBankEros_1_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                               z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
                               z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
                               z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
                               z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
                               z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
                               z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength,
                               z.n42, z.n54, z.n85, z.UrbBankStab)[Y][i] * (z.SedPhos / 1000000) * z.BankPFrac

        # CALCULATIONS FOR STREAM BANK STABILIZATION AND FENCING
        # z.SURBBANK = 0
        # z.NURBBANK = 0
        z.PURBBANK = 0
        z.FCURBBANK = 0

        # z.SEDSTAB = 0
        # z.SURBBANK = 0 # TODO: Why is this in here twice ?

        # if z.n42b > 0:
        #     z.SEDSTAB = (z.n46c / z.n42b) * z.StreamBankEros[Y][i] * z.n85d
        #     z.SURBBANK = (z.UrbBankStab / z.n42b) * z.StreamBankEros[Y][i] * z.n85d

        # z.SEDFEN = 0
        # if z.n42 > 0:
        #     z.SEDFEN = (z.n45 / z.n42) * z.StreamBankEros[Y][i] * z.AGSTRM * z.n85

        # print("SURBBANK orig = ", z.SURBBANK, "SURBBANK new = ", z.SURBBANK_temp[Y][i])
        # print(z.SURBBANK == z.SURBBANK_temp[Y][i])

        # print("SEDSTAB orig = ", z.SEDSTAB, "SEDSTAB new = ", z.SURBBANK_temp[Y][i])
        # print(z.SEDSTAB == z.SURBBANK_temp[Y][i])

        # z.StreamBankEros[Y][i] = z.StreamBankEros[Y][i] - (z.SEDSTAB[Y][i] + z.SEDFEN[Y][i] + z.SURBBANK[Y][i])
        # if z.StreamBankEros[Y][i] < 0:
        #     z.StreamBankEros[Y][i] = 0

        # z.NSTAB = 0
        # z.NURBBANK = 0
        # if z.n42b > 0:
        # z.NSTAB = (z.n46c / z.n42b) * \
        #           StreamBankN(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
        #                       z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
        #                       z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
        #                       z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
        #                       z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
        #                       z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
        #                       z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength,
        #                       z.n42, z.n54, z.n85, z.UrbBankStab, z.SedNitr, z.BankNFrac)[Y][i] * z.n69c
        # z.NURBBANK = (z.UrbBankStab / z.n42b) * StreamBankN(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
        #                       z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
        #                       z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
        #                       z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
        #                       z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
        #                       z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
        #                       z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength,
        #                       z.n42, z.n54, z.n85, z.UrbBankStab, z.SedNitr, z.BankNFrac)[Y][i] * z.n69c

        # z.NFEN = 0
        # if z.n42 > 0:
        #     z.NFEN = (z.n45 / z.n42) * StreamBankN(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
        #                           z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
        #                           z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
        #                           z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
        #                           z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
        #                           z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
        #                           z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength,
        #                           z.n42, z.n54, z.n85, z.UrbBankStab, z.SedNitr, z.BankNFrac)[Y][i] * AGSTRM_2(z.AgLength, z.StreamLength) * z.n69

        # z.StreamBankN_1[Y][i] = StreamBankN(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
        #                           z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
        #                           z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
        #                           z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
        #                           z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
        #                           z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
        #                           z.AvSlope, z.SedAAdjust, z.StreamLength, z.SedNitr, z.BankNFrac)[Y][i] - (z.NSTAB + z.NFEN + z.NURBBANK)
        # if z.StreamBankN_1[Y][i] < 0:
        #     z.StreamBankN_1[Y][i] = 0

        z.PSTAB = 0
        z.PURBBANK = 0
        if z.n42b > 0:
            z.PSTAB = (z.n46c / z.n42b) * z.StreamBankP[Y][i] * z.n77c
            z.PURBBANK = (z.UrbBankStab / z.n42b) * z.StreamBankP[Y][i] * z.n77c

        z.PFEN = 0
        if z.n42 > 0:
            z.PFEN = (z.n45 / z.n42) * z.StreamBankP[Y][i] * AGSTRM_2(z.AgLength, z.StreamLength) * z.n77

        z.StreamBankP[Y][i] = z.StreamBankP[Y][i] - (z.PSTAB + z.PFEN + z.PURBBANK)
        if z.StreamBankP[Y][i] < 0:
            z.StreamBankP[Y][i] = 0

        # CALCULATE ANNUAL STREAMBANK N AND P AND SEDIMENT
        # z.StreamBankNSum[Y] += z.StreamBankN_1[Y][i]
        z.StreamBankPSum[Y] += z.StreamBankP[Y][i]
        z.StreamBankErosSum[Y] += \
            StreamBankEros_1_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                               z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0,
                               z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0, z.RecessionCoef, z.SeepCoef
                               , z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                               z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj,
                               z.SedAFactor_0, z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d,
                               z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab)[Y][i]

        # GROUNDWATER N LOADS ARE REDUCED BASED ON SPECIFIC BMPS
        z.GWNRF = 0
        z.CHNGN1 = 0
        z.CHNGN2 = 0
        z.CHNGN3 = 0
        z.CHNGN4 = 0
        z.CHNGN5 = 0
        z.CHNGNTOT = 0
        z.PCTN1 = 0
        z.PCTN2 = 0
        z.PCTN3 = 0
        z.PCTN4 = 0
        z.PCBMPAC = 0
        z.HPBMPAC = 0
        z.BMPACRES = 0
        z.PCTAG = 0
        z.RCNMAC = 0
        z.HPNMAC = 0

        z.CHNGN1 = z.n25 / 100
        z.CHNGN2 = z.n26 / 100
        z.CHNGN3 = z.n27 / 100
        z.CHNGN4 = z.n27b / 100
        z.CHNGN5 = z.n28 / 100
        z.CHNGNTOT = z.CHNGN1 + z.CHNGN2 + z.CHNGN3 + z.CHNGN4 + z.CHNGN5

        if AreaTotal_2(z.Area) > 0 and z.n23 > 0 and z.n42 > 0 and z.n42b > 0:
            z.PCTAG = (z.n23 + z.n24) / AreaTotal_2(z.Area)
            z.GroundNitr[Y][i] -= z.GroundNitr[Y][i] * ((z.n28b / 100) * z.n23) / z.n23 * z.PCTAG * z.n70
            z.GroundNitr[Y][i] -= z.GroundNitr[Y][i] * (z.n43 / z.n42) * (z.n42 / z.n42b) * z.PCTAG * z.n64
            z.GroundNitr[Y][i] -= (z.GroundNitr[Y][i] * (
                    (((z.n29 / 100) * z.n23) + ((z.n37 / 100) * z.n24)) / (z.n23 + z.n24))) * z.PCTAG * z.n68

        # Groundwater P loads are reduced based on extent of nutrient management BMP
        z.RCNMAC = (z.n28b / 100) * z.n23
        z.HPNMAC = (z.n35b / 100) * z.n24

        if AreaTotal_2(z.Area) > 0:
            z.GroundPhos[Y][i] -= (((z.RCNMAC + z.HPNMAC) / AreaTotal_2(z.Area)) *
                                   z.GroundPhos[Y][i] * z.n78)

        z.GroundNitrSum[Y] += z.GroundNitr[Y][i]
        z.GroundPhosSum[Y] += z.GroundPhos[Y][i]

        z.TileDrainSum[Y] += \
            TileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                        z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                        z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
                        z.RecessionCoef, z.SeepCoef, z.Landuse,
                        z.TileDrainDensity)[Y][i]
        z.TileDrainNSum[Y] += z.TileDrainN[Y][i]
        z.TileDrainPSum[Y] += z.TileDrainP[Y][i]
        z.TileDrainSedSum[Y] += z.TileDrainSed[Y][i]
        # z.AnimalNSum[Y] += z.AnimalN[Y][i]
        z.AnimalPSum[Y] += z.AnimalP[Y][i]
        z.AnimalFCSum[Y] += z.AnimalFC[Y][i]
        z.WWOrgsSum[Y] += z.WWOrgs[Y][i]
        z.SSOrgsSum[Y] += z.SSOrgs[Y][i]
        z.UrbOrgsSum[Y] += z.UrbOrgs[Y][i]
        z.TotalOrgsSum[Y] += z.TotalOrgs[Y][i]
        z.WildOrgsSum[Y] += z.WildOrgs[Y][i]

        # z.GRLostBarnNSum[Y] += z.GRLostBarnN[Y][i]
        z.GRLostBarnPSum[Y] += z.GRLostBarnP[Y][i]
        z.GRLostBarnFCSum[Y] += z.GRLostBarnFC[Y][i]
        # z.NGLostBarnNSum[Y] += z.NGLostBarnN[Y][i]
        z.NGLostBarnPSum[Y] += z.NGLostBarnP[Y][i]
        z.NGLostBarnFCSum[Y] += z.NGLostBarnFC[Y][i]
        z.NGLostManPSum[Y] += z.NGLostManP[Y][i]

        z.TotNitr[Y][i] += StreamBankN_1_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                           z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
                                           z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
                                           z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
                                           z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
                                           z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
                                           z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.AgLength,
                                           z.UrbBankStab, z.SedNitr, z.BankNFrac, z.n69c, z.n45, z.n69)[Y][i] + \
                           z.TileDrainN[Y][i] +  AnimalN_2(z.NYrs, z.NGPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN, z.NGAppNRate, z.Prec, z.DaysMonth,
            z.NGPctSoilIncRate, z.GRPctManApp, z.GRAppNRate, z.GRPctSoilIncRate, z.NGBarnNRate, z.AWMSNgPct, z.NgAWMSCoeffN,
            z.RunContPct, z.RunConCoeffN, z.PctGrazing, z.GRBarnNRate, z.AWMSGrPct, z.GrAWMSCoeffN, z.PctStreams, z.GrazingNRate)[Y][i]
        z.TotPhos[Y][i] += z.StreamBankP[Y][i] + z.TileDrainP[Y][i] + z.AnimalP[Y][i]
        z.TotNitrSum[Y] += StreamBankN_1_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                           z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
                                           z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
                                           z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
                                           z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
                                           z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
                                           z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.AgLength,
                                           z.UrbBankStab, z.SedNitr, z.BankNFrac, z.n69c, z.n45, z.n69)[Y][i] + \
                           z.TileDrainN[Y][i] + AnimalN_2(z.NYrs, z.NGPctManApp, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN, z.NGAppNRate, z.Prec, z.DaysMonth,
            z.NGPctSoilIncRate, z.GRPctManApp, z.GRAppNRate, z.GRPctSoilIncRate, z.NGBarnNRate, z.AWMSNgPct, z.NgAWMSCoeffN,
            z.RunContPct, z.RunConCoeffN, z.PctGrazing, z.GRBarnNRate, z.AWMSGrPct, z.GrAWMSCoeffN, z.PctStreams, z.GrazingNRate)[Y][i]
        z.TotPhosSum[Y] += z.StreamBankP[Y][i] + z.TileDrainP[Y][i] + z.AnimalP[Y][i]



@memoize
def StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                   Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                   GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                   StreamLength):
    result = np.zeros((NYrs, 12))
    le = LE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
            Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
            NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = le[Y][i] * StreamLength * 1500 * 1.5
    return result


@memoize
def StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                     Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                     GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                     SedAAdjust, StreamLength):
    le = LE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
              , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal
              , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust)
    return le * StreamLength * 1500 * 1.5



@memoize
def StreamBankEros_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                     ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                     Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                     GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                     SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab):
    result = np.zeros((NYrs, 12))
    streambankeros = StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                    Grow_0,
                                    CNP_0, Imper,
                                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                    RecessionCoef, SeepCoef
                                    , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                    StreamWithdrawal, GroundWithdrawal
                                    , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                    SedAAdjust, StreamLength)
    sedstab = SEDSTAB(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                      CNP_0, Imper,
                      ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                      RecessionCoef, SeepCoef
                      , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                      StreamWithdrawal, GroundWithdrawal
                      , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                      SedAAdjust, StreamLength, n42b, n46c, n85d)
    sedfen = SEDFEN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                    CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                    RecessionCoef, SeepCoef
                    , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                    StreamWithdrawal, GroundWithdrawal
                    , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                    SedAAdjust, StreamLength, AgLength, n42, n45, n85)
    surbbank = SURBBANK(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                        Imper,
                        ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
                        , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                        GroundWithdrawal
                        , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
                        StreamLength
                        , UrbBankStab, n42b, n85d)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = streambankeros[Y][i] - (sedstab[Y][i] + sedfen[Y][i] + surbbank[Y][i])
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result

@memoize
def StreamBankEros_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                       Imper,
                       ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                       Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                       GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                       SedAAdjust, StreamLength, n42b, n46c, n85d, AgLength, n42, n45, n85, UrbBankStab):
    streambankeros = StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                             AntMoist_0, Grow_0,
                                             CNP_0, Imper,
                                             ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                             RecessionCoef, SeepCoef
                                             , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                             StreamWithdrawal, GroundWithdrawal
                                             , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                             SedAAdjust, StreamLength)
    sedstab = SEDSTAB_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                        CNP_0, Imper,
                        ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                        RecessionCoef, SeepCoef
                        , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                        StreamWithdrawal, GroundWithdrawal
                        , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                        SedAAdjust, StreamLength, n42b, n46c, n85d)
    sedfen = SEDFEN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                      CNP_0, Imper,
                      ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                      RecessionCoef, SeepCoef
                      , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                      StreamWithdrawal, GroundWithdrawal
                      , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                      SedAAdjust, StreamLength, AgLength, n42, n45, n85)
    surbbank = SURBBANK_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                          SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                          StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0,
                          AvKF, AvSlope, SedAAdjust, StreamLength, UrbBankStab, n42b, n85d)
    return np.maximum(streambankeros - (sedstab + sedfen + surbbank), 0)


@memoize
def StreamBankN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                AvSlope, SedAAdjust, StreamLength,SedNitr, BankNFrac):
    result = np.zeros((NYrs, 12))
    stream_bank_eros_2 = StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                          UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                          TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                          NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                          AvSlope, SedAAdjust, StreamLength)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = stream_bank_eros_2[Y][i] * (SedNitr / 1000000) * BankNFrac
    return result

def StreamBankN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                AvSlope, SedAAdjust, StreamLength,SedNitr, BankNFrac):
    return StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                        CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                        UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                        RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                        TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                        NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                        AvSlope, SedAAdjust, StreamLength) * (SedNitr / 1000000) * BankNFrac



@memoize
def StreamBankNSum(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                   CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                   UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                   RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                   TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                   NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                   AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                   UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69):
    result = np.zeros((NYrs,))
    streambank_n_1 = StreamBankN_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                   CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                   UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                   RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                   TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                   NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                   AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                                   UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69)
    for Y in range(NYrs):
        for i in range(12):
            result[Y] += streambank_n_1[Y][i]

    return result


def StreamBankNSum_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                     CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                     UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                     RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                     TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                     NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                     AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                     UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69):
    return np.sum(StreamBankN_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                  CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                  UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                  TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                  NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                  AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                                  UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69), axis=1)



@memoize
def StreamBankN_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                  CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                  UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                  TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                  NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                  AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                  UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69):
    result = np.zeros((NYrs, 12))
    streambank_n = StreamBankN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                               CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                               UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                               RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                               TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                               NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                               AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)
    nstab = NSTAB(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                  CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                  UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                  TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                  NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                  AvSlope, SedAAdjust, StreamLength, AgLength,
                  UrbBankStab, SedNitr, BankNFrac, n69c)

    nfen = NFEN(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                AvSlope, SedAAdjust, StreamLength, AgLength,
                UrbBankStab, SedNitr, BankNFrac, n45, n69)

    nurbbank = NURBBANK(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                        CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                        UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                        RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                        TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                        NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                        AvSlope, SedAAdjust, StreamLength, n42b, UrbBankStab, SedNitr, BankNFrac, n69c)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = streambank_n[Y][i] - (nstab[Y][i] + nfen[Y][i] + nurbbank[Y][i])
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result

@memoize
def StreamBankN_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                    CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                    UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                    RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                    TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                    NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                    AvSlope, SedAAdjust, StreamLength, n42b, AgLength,
                    UrbBankStab, SedNitr, BankNFrac, n69c, n45, n69):
    streambank_n = StreamBankN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                                 CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                                 UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                 RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                                 TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                                 NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                                 AvSlope, SedAAdjust, StreamLength, SedNitr, BankNFrac)
    nstab = NSTAB_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                    CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                    UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                    RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                    TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                    NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                    AvSlope, SedAAdjust, StreamLength, AgLength, UrbBankStab, SedNitr, BankNFrac, n69c)

    nfen = NFEN_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                  CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                  UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                  TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                  NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                  AvSlope, SedAAdjust, StreamLength, AgLength, UrbBankStab, SedNitr, BankNFrac, n45, n69)

    nurbbank = NURBBANK_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area,
                          CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, CN,
                          UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                          RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse,
                          TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal,
                          NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF,
                          AvSlope, SedAAdjust, StreamLength, n42b, UrbBankStab, SedNitr, BankNFrac, n69c)

    return np.maximum(streambank_n - (nstab + nfen + nurbbank), 0)



@memoize
def StreamFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
               ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
               , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
               GroundWithdrawal):
    result = np.zeros((NYrs, 12))
    flow = Flow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef)
    runoff = Runoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity)
    groundwatle_2 = GroundWatLE_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper,
                                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef, Landuse, TileDrainDensity)
    ptsrcflow = PtSrcFlow(NYrs, PointFlow)
    tiledrain = TileDrain(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper,
                          ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                          SeepCoef, Landuse, TileDrainDensity)
    withdrawal = Withdrawal(NYrs, StreamWithdrawal, GroundWithdrawal)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + flow[Y][i][j]  # This is weird, it seems to be immediately overwritten
                result[Y][i] = (runoff[Y][i]
                                + groundwatle_2[Y][i]
                                + ptsrcflow[Y][i]
                                + tiledrain[Y][i]
                                - withdrawal[Y][i])
    return result

@memoize
def StreamFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                 ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                 Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                 GroundWithdrawal):
    runoff = Runoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                      ISRR, ISRA, Qretention, PctAreaInfil, n25b, CN, Landuse, TileDrainDensity)
    groundwatle_2 = GroundWatLE_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef, Landuse, TileDrainDensity)
    ptsrcflow = PtSrcFlow_2(NYrs, PointFlow)
    tiledrain = TileDrain_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                            RecessionCoef,
                            SeepCoef, Landuse, TileDrainDensity)
    withdrawal = Withdrawal_2(NYrs, StreamWithdrawal, GroundWithdrawal)
    return runoff + groundwatle_2 + ptsrcflow + tiledrain - withdrawal



@memoize
def StreamFlowLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                 ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
                 , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                 GroundWithdrawal):
    result = np.zeros((NYrs, 12))
    streamflow = StreamFlow(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper,
                            ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                            SeepCoef
                            , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                            GroundWithdrawal)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = streamflow[Y][i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result

def StreamFlowLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                   Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                   GroundWithdrawal):
    streamflow = StreamFlow_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                              RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                              PointFlow, StreamWithdrawal, GroundWithdrawal)
    return np.where(streamflow > 0, streamflow, 0)



@memoize
def StreamFlowVol(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
                  , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                  GroundWithdrawal):
    # CALCULATE THE VOLUMETRIC STREAM Flow
    result = np.zeros((NYrs, 12))
    streamflowle = StreamFlowLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper,
                                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                                SeepCoef
                                , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                StreamWithdrawal, GroundWithdrawal)
    totareameters = TotAreaMeters(NRur, NUrb, Area)
    for Y in range(NYrs):
        for i in range(12):
            # CALCULATE THE VOLUMETRIC STREAM Flow
            result[Y][i] = ((streamflowle[Y][i] / 100) * totareameters) / (86400 * DaysMonth[Y][i])
    return result


def StreamFlowVol_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                    Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
                    GroundWithdrawal):
    streamflowle = StreamFlowLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                  RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                                  PointFlow, StreamWithdrawal, GroundWithdrawal)
    totareameters = TotAreaMeters(NRur, NUrb, Area)
    return streamflowle / 100 * totareameters / (86400 * DaysMonth)



# @memoize
def SURBBANK(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
             ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef
             , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal, GroundWithdrawal
             , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength
             , UrbBankStab, n42b, n85d):
    result = np.zeros((NYrs, 12))
    streambankeros = StreamBankEros(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                    CNP_0, Imper,
                                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                    RecessionCoef, SeepCoef
                                    , Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow,
                                    StreamWithdrawal, GroundWithdrawal
                                    , NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope,
                                    SedAAdjust, StreamLength)
    for Y in range(NYrs):
        for i in range(12):
            if n42b > 0:
                result[Y][i] = (UrbBankStab / n42b) * streambankeros[Y][i] * n85d
    return result

def SURBBANK_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
               ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
               Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity, PointFlow, StreamWithdrawal,
               GroundWithdrawal, NumAnimals, AvgAnimalWt, StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust,
               StreamLength, UrbBankStab, n42b, n85d):
    streambankeros = StreamBankEros_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                    CNP_0, Imper,
                                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                    RecessionCoef, SeepCoef, Qretention, PctAreaInfil, n25b, Landuse, TileDrainDensity,
                                    PointFlow, StreamWithdrawal, GroundWithdrawal, NumAnimals, AvgAnimalWt,
                                    StreamFlowVolAdj, SedAFactor_0, AvKF, AvSlope, SedAAdjust, StreamLength)
    if n42b > 0:
        return (UrbBankStab / n42b) * streambankeros * n85d
    else:
        return np.zeros((NYrs, 12))



@memoize
def SurfaceLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed):
    result = np.zeros((NYrs, 12, 31, 16, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0,
                                        Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    nlu = NLU_function(NRur, NUrb)
    washimperv = WashImperv(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, AntMoist_0, Grow_0, NRur, NUrb)
    washperv = WashPerv(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNP_0, AntMoist_0, Grow_0, NRur, NUrb)
    lu_1 = LU_1(NRur, NUrb)
    urbloadred = UrbLoadRed(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                            Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                if Area[l] > 0:
                                    result[Y][i][j][l][q] = (((LoadRateImp[l][q] * washimperv[Y][i][j][l] * (
                                            (Imper[l] * (1 - ISRR[lu_1[l]]) * (1 - ISRA[lu_1[l]]))
                                            # * (SweepFrac[i] + (
                                            # (1 - SweepFrac[i]) * ((1 - UrbSweepFrac) * Area[l]) / Area[l]))
                                            * 1)  # TODO For some reason, this commented out code always needs to evaluate to 1 in order for the separation to occur
                                                               + LoadRatePerv[l][q] * washperv[Y][i][j][l] * (
                                                                       1 - (Imper[l] * (1 - ISRR[lu_1[l]]) * (
                                                                       1 - ISRA[lu_1[l]]))))
                                                              * Area[l]) - urbloadred[Y][i][j][l][q])
                                else:
                                    result[Y][i][j][l][q] = 0

                                if result[Y][i][j][l][q] < 0:
                                    result[Y][i][j][l][q] = 0
                                else:
                                    pass
                    else:
                        pass
                else:
                    pass
    return result

@memoize
def SurfaceLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                  Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp,
                  LoadRatePerv, Storm, UrbBMPRed):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu - NRur, Nqual))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                          Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    # print(np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001)).shape)
    nonzeroday = np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001))
    washimperv = np.reshape(
        np.repeat(
            WashImperv_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, AntMoist_0, Grow_0, NRur, NUrb)[:, :, :,
            NRur:],
            repeats=Nqual,
            axis=3), (NYrs, 12, 31, nlu - NRur, Nqual))
    washperv = np.reshape(
        np.repeat(
            WashPerv_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNP_0, AntMoist_0, Grow_0, NRur, NUrb)[:, :, :, NRur:],
            repeats=Nqual,
            axis=3), (NYrs, 12, 31, nlu - NRur, Nqual))
    urbloadred = UrbLoadRed_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                              CNP_0,
                              Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed)[:, :, :, NRur:]

    # area = np.reshape(np.repeat(Area, repeats=NYrs * 12 * 31), (NYrs, 12, 31, nlu))[NRur:]
    temp = np.reshape(np.repeat(Imper[NRur:] * (1 - ISRR) * (1 - ISRA), repeats=Nqual, axis=0), (-1, Nqual))
    # print((washimperv * LoadRateImp).shape)
    # making an assumption that Area cannot be negative. Therefor where area = 0 result will be <= 0 and will be set to zero before returned (eliminating an if)
    result[nonzeroday] = (washimperv[nonzeroday] * LoadRateImp[NRur:] * temp +
                          washperv[nonzeroday] * LoadRatePerv[NRur:] * (1 - temp)) * np.reshape(
        np.repeat(Area[NRur:], repeats=Nqual, axis=0), (nlu - NRur, Nqual)) - urbloadred[nonzeroday]
    return np.maximum(result, 0)



@memoize
def SurfaceLoad_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                  Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
                  FilterWidth, PctStrmBuf):
    result = np.zeros((NYrs, 12, 31, 16, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    nlu = NLU_function(NRur, NUrb)
    adjurbanqtotal_1 = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0,
                                        Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    surfaceload = SurfaceLoad(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                              CNP_0,
                              Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm,
                              UrbBMPRed)
    retentioneff = RetentionEff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0,
                                AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, PctAreaInfil)
    filtereff = FilterEff(FilterWidth)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if adjurbanqtotal_1[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                result[Y][i][j][l][q] = surfaceload[Y][i][j][l][q] * ((1 - retentioneff) * (
                                        1 - (filtereff * PctStrmBuf)))
                    else:
                        pass
                else:
                    pass
    return result


def SurfaceLoad_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                    Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
                    FilterWidth, PctStrmBuf):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu - NRur, Nqual))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal_1 = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                          Grow_0, CNP_0,
                                          Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    surfaceload = SurfaceLoad_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, LoadRateImp, LoadRatePerv, Storm,
                                UrbBMPRed)
    retentioneff = RetentionEff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, Qretention, NRur, NUrb, Area, CNI_0,
                                  AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, PctAreaInfil)
    filtereff = FilterEff_2(FilterWidth)
    nonzero = np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal_1 > 0.001))
    result[nonzero] = surfaceload[nonzero] * ((1 - retentioneff) * (1 - (filtereff * PctStrmBuf)))
    return result



# @memoize
def TileDrain(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef, Landuse,
              TileDrainDensity):
    result = np.zeros((NYrs, 12))
    tiledrainro = TileDrainRO(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area,
                              TileDrainDensity)
    tiledraingw = TileDrainGW(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                              Imper,
                              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                              SeepCoef, Landuse, TileDrainDensity)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (result[Y][i] + tiledrainro[Y][i] + tiledraingw[Y][i])
    return result

@memoize
def TileDrain_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                Landuse, TileDrainDensity):
    tiledrainro = TileDrainRO_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse,
                                Area,
                                TileDrainDensity)
    tiledraingw = TileDrainGW_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0,
                                Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0,
                                RecessionCoef, SeepCoef, Landuse, TileDrainDensity)
    return tiledrainro + tiledraingw


@memoize
def TileDrainGW(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                Landuse, TileDrainDensity):
    result = np.zeros((NYrs, 12))
    gwagle = GwAgLE(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                    ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                    Landuse)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (result[Y][i] + [gwagle[Y][i] * TileDrainDensity])
    return result


def TileDrainGW_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef, SeepCoef,
                  Landuse, TileDrainDensity):
    if (TileDrainDensity > 0):
        gwagle = GwAgLE_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                          Imper, ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap, SatStor_0, RecessionCoef,
                          SeepCoef, Landuse)
        return gwagle * TileDrainDensity
    else:
        return np.zeros((NYrs, 12))


# @time_function
@memoize
def TileDrainRO(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area,
                TileDrainDensity):
    result = np.zeros((NYrs, 12))
    ag_runoff = AgRunoff(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            # CALCULATE THE SURFACE RUNOFF PORTION OF TILE DRAINAGE
            result[Y][i] = ag_runoff[Y][i] * TileDrainDensity
    return result

# @time_function
@memoize
def TileDrainRO_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area,
                TileDrainDensity):
    return AgRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, CN, AntMoist_0, NUrb, Grow_0, Landuse, Area) * TileDrainDensity


def reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return np.mean(data[s < m])


def time_function(method):
    def timed(*args, **kw):
        """return the result of the function as well as timing results for it"""

        def reset_scope():
            method.result = {}  # for memoized functions

        function_to_time = timeit.Timer(lambda: method(*args), setup=reset_scope)
        runs = function_to_time.repeat(number=1, repeat=100)
        print("300 loops of %r, average time per loop: %f, best: %f, worst: %f" % (
            method.__name__, reject_outliers(np.array(runs)), np.min(runs), np.max(runs)))

        result = method(*args, **kw)
        return result

    return timed



def TotAEU(NumAnimals, AvgAnimalWt):
    result = 0
    aeu1 = ((NumAnimals[2] / 2) * (AvgAnimalWt[2]) / 1000) + ((NumAnimals[3] / 2) * (AvgAnimalWt[3]) / 1000)
    aeu2 = (NumAnimals[7] * AvgAnimalWt[7]) / 1000
    aeu3 = (NumAnimals[5] * AvgAnimalWt[5]) / 1000
    aeu4 = (NumAnimals[4] * AvgAnimalWt[4]) / 1000
    aeu5 = (NumAnimals[6] * AvgAnimalWt[6]) / 1000
    aeu6 = (NumAnimals[0] * AvgAnimalWt[0]) / 1000
    aeu7 = (NumAnimals[1] * AvgAnimalWt[1]) / 1000
    result += aeu1 + aeu2 + aeu3 + aeu4 + aeu5 + aeu6 + aeu7
    return result


def TotAEU_2(NumAnimals, AvgAnimalWt):
    aeu = NumAnimals * AvgAnimalWt / 1000
    aeu[2:4] /= 2
    return np.sum(aeu)



@memoize
def TotAreaMeters(NRur, NUrb, Area):
    result = 0.0
    areatotal = AreaTotal(NRur, NUrb, Area)
    result = areatotal * 10000
    return result



def TotLAEU(NumAnimals, AvgAnimalWt):
    result = 0
    aeu3 = (NumAnimals[5] * AvgAnimalWt[5]) / 1000
    aeu4 = (NumAnimals[4] * AvgAnimalWt[4]) / 1000
    aeu5 = (NumAnimals[6] * AvgAnimalWt[6]) / 1000
    aeu6 = (NumAnimals[0] * AvgAnimalWt[0]) / 1000
    aeu7 = (NumAnimals[1] * AvgAnimalWt[1]) / 1000
    result += aeu3 + aeu4 + aeu5 + aeu6 + aeu7
    return result


def TotLAEU_2(NumAnimals, AvgAnimalWt):
    return np.sum(NumAnimals[[0, 1, 4, 5, 6]] * AvgAnimalWt[[0, 1, 4, 5, 6]] / 1000)



def TotPAEU(NumAnimals, AvgAnimalWt):
    result = 0
    aeu1 = ((NumAnimals[2] / 2) * (AvgAnimalWt[2]) / 1000) + ((NumAnimals[3] / 2) * (AvgAnimalWt[3]) / 1000)
    aeu2 = (NumAnimals[7] * AvgAnimalWt[7]) / 1000
    result += aeu1 + aeu2
    return result


def TotPAEU_2(NumAnimals, AvgAnimalWt):
    return (NumAnimals[2] / 2 * AvgAnimalWt[2] + NumAnimals[3] / 2 * AvgAnimalWt[3] + NumAnimals[7] * AvgAnimalWt[
        7]) / 1000



# @memoize
# def UncontrolledQ(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, CNP_0, AntMoist_0, Grow_0, Imper, ISRR, ISRA):
#     result = 0
#     water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
#     nlu = NLU(NRur, NUrb)
#     areatotal = AreaTotal(NRur, NUrb, Area)
#     qruni = QrunI(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
#     qrunp = QrunP(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
#     lu = LU(NRur, NUrb)
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
#                     if water[Y][i][j] < 0.05:
#                         pass
#                     else:
#                         for l in range(NRur, nlu):
#                             if areatotal > 0:
#                                 result += ((qruni[Y][i][j][l] * (Imper[l] * (1 - ISRR[lu[l]]) *
#                                       (1 - ISRA[lu[l]])) + qrunp[Y][i][j][l] *
#                                       (1 - (Imper[l] * (1 - ISRR[lu[l]]) * (1 - ISRA[lu[l]])))) *
#                                                     Area[l] / areatotal)
#                 else:
#                     pass
#
#     return result
#
#
# def UncontrolledQ_2():
#     pass


try:
    from UnsatStor_inner_compiled import UnsatStor_inner
except ImportError:
    print("Unable to import compiled UnsatStor_inner, using slower version")
    from UnsatStor_inner import UnsatStor_inner


@memoize
def UnsatStor(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
              ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    result = np.zeros((NYrs, 12, 31))
    infiltration = Infiltration(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper,
                                ISRR, ISRA, CN)
    unsatstor_carryover = UnsatStor_0
    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = unsatstor_carryover
                result[Y][i][j] = result[Y][i][j] + infiltration[Y][i][j]
                if et[Y][i][j] >= result[Y][i][j]:
                    result[Y][i][j] = 0
                else:
                    result[Y][i][j] = result[Y][i][j] - et[Y][i][j]
                if result[Y][i][j] > MaxWaterCap:
                    result[Y][i][j] = MaxWaterCap
                else:
                    pass
                unsatstor_carryover = result[Y][i][j]
    return result


# NYrs = arg(0, name=NYrs)  :: int64
#   DaysMonth = arg(1, name=DaysMonth)  :: array(int32, 2d, C)
#   MaxWaterCap = arg(2, name=MaxWaterCap)  :: float64
#   UnsatStor_0 = arg(3, name=UnsatStor_0)  :: float64
#   infiltration = arg(4, name=infiltration)  :: array(float64, 3d, C)
#   et = arg(5, name=et)  :: array(float64, 3d, C)

# @jit(cache=True, nopython=True)
# @compiled


@memoize
def UnsatStor_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA, CN, UnsatStor_0, KV, PcntET, DayHrs, MaxWaterCap):
    infiltration = Infiltration_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA, CN)
    et = DailyET_2(Temp, KV, PcntET, DayHrs)
    return UnsatStor_inner(NYrs, DaysMonth, MaxWaterCap, UnsatStor_0, infiltration, et)[0]


# @time_function
@memoize
def UrbanQTotal(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR,
                ISRA):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urb_area_total = UrbAreaTotal(NRur, NUrb, Area)
    qrun_i = QrunI(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
    qrun_p = QrunP(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
    lu = LU(NRur, NUrb)

    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            if urb_area_total > 0:
                                result[Y][i][j] += (
                                            (qrun_i[Y][i][j][l] * (Imper[l] * (1 - ISRR[lu[l]]) * (1 - ISRA[lu[l]]))
                                             + qrun_p[Y][i][j][l] *
                                             (1 - (Imper[l] * (1 - ISRR[lu[l]]) * (1 - ISRA[lu[l]]))))
                                            * Area[l] / urb_area_total)
    return result

# @time_function
@memoize
def UrbanQTotal_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper, ISRR,
                ISRA):
    result = np.zeros((NYrs, 12, 31))
    urb_area_total = UrbAreaTotal(NRur, NUrb, Area)
    qrun_i = QrunI_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
    qrun_p = QrunP_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
    z= np.zeros((10,))
    ISRR = np.hstack((z,ISRR))
    ISRA = np.hstack((z,ISRA))
    x = (Imper * (1 - ISRR) * (1 - ISRA))
    temp = (qrun_i * x + qrun_p * (1- x)) * Area
    if urb_area_total>0:
        result = np.sum(temp, axis=3)/urb_area_total
    return result

@memoize
def UrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA):
    result = np.zeros((NYrs, 12, 31))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urban_area_total = UrbAreaTotal(NRur, NUrb, Area)
    area_total = AreaTotal(NRur, NUrb, Area)
    urban_q_total = UrbanQTotal(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper, ISRR, ISRA)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if urban_area_total > 0:
                        result[Y][i][j] = urban_q_total[Y][i][j] * urban_area_total / area_total
                    else:
                        result[Y][i][j] = 0
    return result

@memoize
def UrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                  ISRR, ISRA):
    urban_area_total = UrbAreaTotal(NRur, NUrb, Area)
    area_total = AreaTotal(NRur, NUrb, Area)
    urban_q_total = UrbanQTotal_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper, ISRR, ISRA)
    return urban_q_total * urban_area_total / area_total


@memoize
def UrbanRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                ISRR, ISRA):
    result = np.zeros((NYrs, 12))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urbanqtotal_1 = UrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper,
                                  ISRR, ISRA)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i] += urbanqtotal_1[Y][i][j]
                else:
                    pass
    return result


def UrbanRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                  CNP_0, Imper, ISRR, ISRA):
    return np.sum(UrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                  CNP_0, Imper, ISRR, ISRA), axis=2)


# @time_function
@memoize
def UrbAreaTotal(NRur,NUrb,Area):
    result = 0
    nlu = NLU_function(NRur, NUrb)
    for l in range(NRur, nlu):
        result += Area[l]
    return result


# Tried, it was slower. UrbAreaTotal is faster
# @time_function
#@memoize
def UrbAreaTotal_2(NRur,NUrb,Area):
    nlu = NLU_function(NRur, NUrb)
    return np.sum(Area[NRur:])


# @memoize
def UrbLoadRed(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
               Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed):
    result = np.zeros((NYrs, 12, 31, 16, Nqual))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal = AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                      Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    nlu = NLU_function(NRur, NUrb)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    # result[Y][i][j][l][q] = 0
                    if adjurbanqtotal[Y][i][j] > 0.001:
                        for l in range(NRur, nlu):
                            for q in range(Nqual):
                                if Storm > 0:
                                    result[Y][i][j][l][q] = (water[Y][i][j] / Storm) * UrbBMPRed[l][q]
                                else:
                                    result[Y][i][j][l][q] = 0
                                if water[Y][i][j] > Storm:
                                    result[Y][i][j][l][q] = UrbBMPRed[l][q]
                else:
                    pass
    return result


# UrbLoadRed_2 is faster than UrbLoadRed_1
def UrbLoadRed_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                 Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed):
    if (Storm > 0):
        water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
        adjurbanqtotal = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                            Grow_0, CNP_0,
                                            Imper, ISRR, ISRA, Qretention, PctAreaInfil)
        nlu = NLU_function(NRur, NUrb)
        return UrbLoadRed_inner(NYrs, DaysMonth, Temp, NRur, Nqual, Storm, UrbBMPRed, water, adjurbanqtotal, nlu)
    else:
        return np.zeros((NYrs, 12, 31, 16, Nqual))

def UrbLoadRed_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                 Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed):
    result = np.zeros((NYrs, 12, 31, 16, Nqual))
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    adjurbanqtotal = AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                        Grow_0, CNP_0,
                                        Imper, ISRR, ISRA, Qretention, PctAreaInfil)
    np.repeat(Temp[:, :, :, None, None], NRur, axis=3)
    Temp = np.tile(Temp[:, :, :, None, None], (1, 1, 1, 16, Nqual))
    water = np.tile(water[:, :, :, None, None], (1, 1, 1, 16, Nqual))
    adjurbanqtotal = np.tile(adjurbanqtotal[:, :, :, None, None], (1, 1, 1, 16, Nqual))
    Storm = np.tile(np.array([Storm]), (1, 1, 1, 16, Nqual))
    UrbBMPRed = np.tile(UrbBMPRed, (NYrs, 12, 31, 1, 1))
    temp = (water / Storm) * UrbBMPRed
    result[np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal > 0.001) & (Storm > 0))] = temp[
        np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal > 0.001) & (Storm > 0))]
    result[np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal > 0.001) & (water > Storm))] = UrbBMPRed[
        np.where((Temp > 0) & (water > 0.01) & (adjurbanqtotal > 0.001) & (water > Storm))]
    result[:, :, :, 0:NRur] = 0
    return result

def UrbLoadRed_3(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                 Imper, ISRR, ISRA, Qretention, PctAreaInfil, Nqual, Storm, UrbBMPRed):
    if (Storm > 0):
        result = np.zeros((NYrs, 12, 31, 16, Nqual))
        nlu = NLU_function(NRur, NUrb)
        temp = np.reshape(np.repeat(Temp, repeats=(nlu - NRur) * Nqual, axis=2),(NYrs, 12, 31, nlu - NRur, Nqual))
        water = np.reshape(
            np.repeat(Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec), repeats=(nlu - NRur) * Nqual, axis=2),
            (NYrs, 12, 31, nlu - NRur, Nqual))
        adjurbanqtotal = np.reshape(
            np.repeat(AdjUrbanQTotal_1_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
                                            AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil), repeats=(nlu - NRur) * Nqual, axis=2),
            (NYrs, 12, 31, nlu - NRur, Nqual))

        nonzero = np.where((temp > 0) & (water > 0.01) & (adjurbanqtotal > 0.001))
        # minium takes care of the water > storm condition

        result[nonzero] = np.minimum(water[nonzero] / Storm, 1) * UrbBMPRed
        return result
    else:
        return np.zeros((NYrs, 12, 31, 16, Nqual))


@memoize
def UrbQRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0, AntMoist_0, Grow_0, Imper, ISRR,
               ISRA):
    result = np.zeros((NYrs, 16, 12))
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    qruni = QrunI(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
    qrunp = QrunP(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
    lu = LU(NRur, NUrb)
    for Y in range(NYrs):
        for i in range(12):
            for l in range(nlu):
                result[Y, l, i] = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            result[Y][l][i] += (qruni[Y][i][j][l] * (
                                    Imper[l] * (1 - ISRR[lu[l]]) * (1 - ISRA[lu[l]]))
                                                + qrunp[Y][i][j][l] * (
                                                        1 - (Imper[l] * (1 - ISRR[lu[l]]) * (
                                                        1 - ISRA[lu[l]]))))

                else:
                    pass
    return result

def UrbQRunoff_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, CNI_0, CNP_0, AntMoist_0, Grow_0, Imper, ISRR,
                 ISRA):
    qruni = QrunI_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)[:, :, :, NRur:]
    qrunp = QrunP_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)[:, :, :, NRur:]
    temp = (Imper[NRur:] * (1 - ISRR) * (1 - ISRA))
    return np.sum(qruni * temp+ qrunp * (1 - temp),axis=2)



@memoize
def UrbRunoffLiter(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA):
    result = np.zeros((NYrs, 12))
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    urbareatotal = UrbAreaTotal(NRur, NUrb, Area)
    urbanrunoff = UrbanRunoff(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                              CNP_0, Imper,
                              ISRR, ISRA)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    result[Y][i] = (urbanrunoff[Y][i] / 100) * urbareatotal * 10000 * 1000
                else:
                    pass
    return result


@memoize
def UrbRunoffLiter_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                     CNP_0, Imper, ISRR, ISRA):
    urbareatotal = UrbAreaTotal_2(NRur, NUrb, Area)
    urbanrunoff = UrbanRunoff_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0,
                                CNP_0, Imper, ISRR, ISRA)
    return urbanrunoff / 100 * urbareatotal * 10000 * 1000


# #TODO: this variable is not used
# def UrbSedLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
#                      AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil,
#                      Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
#                      FilterWidth, PctStrmBuf):
#     result = np.zeros((16, 12))
#     nlu = NLU(NRur, NUrb)
#     lu_load = LuLoad(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
#              AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil,
#              Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
#              FilterWidth, PctStrmBuf)
#     for Y in range(NYrs):
#         for i in range(12):
#             # Add in the urban calucation for sediment
#             for l in range(NRur, nlu):
#                 result[l][i] += lu_load[Y][l][2]
#     return result
#
# def UrbSedLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
#            AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil,
#            Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
#            FilterWidth, PctStrmBuf):
#     return np.reshape(np.repeat(np.sum(LuLoad_2(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0,
#            AntMoist_0, Grow_0, CNP_0, Imper, ISRR, ISRA, Qretention, PctAreaInfil,
#            Nqual, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
#            FilterWidth, PctStrmBuf)[:,:,2],axis=0),repeats=12),(-1,12))

try:
    from WashImperv_inner_compiled import WashImperv_inner
except ImportError:
    print("Unable to import compiled WashPerv_inner, using slower version")
    from WashImperv_inner import WashImperv_inner


@memoize
def WashImperv(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, AntMoist_0, Grow_0, NRur, NUrb):
    result = np.zeros((NYrs, 12, 31, 16))
    impervaccum = np.zeros(16)
    carryover = np.zeros(16)
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    qruni = QrunI(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(nlu):
                    impervaccum[l] = carryover[l]
                    impervaccum[l] = (impervaccum[l] * np.exp(-0.12) + (1 / 0.12) * (1 - np.exp(-0.12)))
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            result[Y][i][j][l] = (1 - math.exp(-1.81 * qruni[Y][i][j][l])) * impervaccum[l]
                            impervaccum[l] -= result[Y][i][j][l]
                else:
                    pass
                for l in range(nlu):
                    carryover[l] = impervaccum[l]
    return result

@memoize
def WashImperv_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNI_0, AntMoist_0, Grow_0, NRur, NUrb):
    nlu = NLU_function(NRur, NUrb)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    qruni = QrunI_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNI_0, AntMoist_0, Grow_0)
    return WashImperv_inner(NYrs, DaysMonth, Temp, NRur, nlu, water, qruni)

try:
    from WashPerv_inner_compiled import WashPerv_inner
except ImportError:
    print("Unable to import compiled WashPerv_inner, using slower version")
    from WashPerv_inner import WashPerv_inner


@memoize
def WashPerv(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNP_0, AntMoist_0, Grow_0, NRur, NUrb):
    pervaccum = np.zeros(16)
    nlu = NLU_function(NRur, NUrb)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    qrunp = QrunP(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
    washperv = np.zeros((NYrs, 12, 31, 16))
    carryover = np.zeros(16)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(nlu):
                    pervaccum[l] = carryover[l]
                    pervaccum[l] = (pervaccum[l] * np.exp(-0.12) + (1 / 0.12) * (1 - np.exp(-0.12)))
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    if water[Y][i][j] < 0.05:
                        pass
                    else:
                        for l in range(NRur, nlu):
                            washperv[Y][i][j][l] = (1 - math.exp(-1.81 * qrunp[Y][i][j][l])) * pervaccum[l]
                            pervaccum[l] -= washperv[Y][i][j][l]
                else:
                    pass
                for l in range(nlu):
                    carryover[l] = pervaccum[l]
    return washperv


def WashPerv_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, CNP_0, AntMoist_0, Grow_0, NRur, NUrb):
    nlu = NLU_function(NRur, NUrb)
    water = Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    qrunp = QrunP_2(NYrs, DaysMonth, NRur, NUrb, Temp, InitSnow_0, Prec, CNP_0, AntMoist_0, Grow_0)
    # WashPerv_inner(NYrs, DaysMonth, Temp, NRur, nlu, water, qrunp)
    # print(WashPerv_inner.inspect_types())
    return WashPerv_inner(NYrs, DaysMonth, Temp, NRur, nlu, water, qrunp)


@memoize
def Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    result = np.zeros((NYrs, 12, 31))
    melt_1 = Melt_1(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rain = Rain(NYrs, DaysMonth, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = rain[Y][i][j] + melt_1[Y][i][j]
    return result

@memoize
def Water_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec):
    melt_1 = Melt_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    rain = Rain_2(Temp, Prec)
    return rain + melt_1


# @memoize

def Withdrawal(NYrs, StreamWithdrawal, GroundWithdrawal):
    result = np.zeros((NYrs, 12))
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (result[Y][i] + StreamWithdrawal[i] + GroundWithdrawal[i])
    return result


def Withdrawal_2(NYrs, StreamWithdrawal, GroundWithdrawal):
    return np.reshape(np.repeat(StreamWithdrawal + GroundWithdrawal, NYrs), (NYrs, 12))

# -*- coding: utf-8 -*-





log = logging.getLogger(__name__)

CM_TO_M = 1 / 100
HA_TO_M2 = 10000
KG_TO_MG = 1000000
M3_TO_L = 1000
TONNE_TO_KG = 1000


def WriteOutput(z):
    # DIMENSION VARIABLES FOR PREDICT CALCULATION AND SCENARIO FILE
    AvOtherLuSed = 0
    # AvOtherLuNitr = 0
    AvOtherLuPhos = 0
    TotSewerSys = 0
    TotNormSys = 0
    TotShortSys = 0
    TotSeptSys = 0
    TotAvLuErosion = 0
    AvTotalSed = 0
    AvDisN = 0
    AvTotalN = 0
    AvDisP = 0
    AvTotalP = 0
    n2t = 0
    n6t = 0
    n13t = 0
    n24t = 0

    AreaSum = np.zeros(12)

    # INSERT VALUES FOR BMP SCENARIO FILE FOR PREDICT APPLICATION
    for l in range(z.NLU):
        z.AvLuSedYield[l] = (z.AvLuSedYield[l] * z.RetentFactorSed) * (1 - z.AttenTSS)
        z.AvLuDisNitr[l] = (z.AvLuDisNitr[l] * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake)) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))
        z.AvLuTotNitr[l] = (z.AvLuTotNitr[l] * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake)) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))
        z.AvLuDisPhos[l] = (z.AvLuDisPhos[l] * z.RetentFactorP) * (1 - z.AttenP)
        z.AvLuTotPhos[l] = (z.AvLuTotPhos[l] * z.RetentFactorP) * (1 - z.AttenP)

    # SET THE SCENARIO VALUES TO LANDUSE LOADS
    for l in range(z.NRur):
        if z.Landuse[l] is LandUse.HAY_PAST:
            z.n2 = z.AvLuSedYield[l]
            z.n6 = z.AvLuTotNitr[l]
            z.n13 = z.AvLuTotPhos[l]
            z.n6dn = z.AvLuDisNitr[l]
            z.n13dp = z.AvLuDisPhos[l]
            z.n24 = round(z.Area[l])
        elif z.Landuse[l] is LandUse.CROPLAND:
            z.n1 = z.AvLuSedYield[l]
            z.n5 = z.AvLuTotNitr[l]
            z.n12 = z.AvLuTotPhos[l]
            z.n5dn = z.AvLuDisNitr[l]
            z.n12dp = z.AvLuDisPhos[l]
            z.n23 = round(z.Area[l])
        elif z.Landuse[l] is LandUse.TURFGRASS:
            z.n2t = z.AvLuSedYield[l]
            z.n6t = z.AvLuTotNitr[l]
            z.n13t = z.AvLuTotPhos[l]
            z.n24t = round(z.Area[l])
        elif z.Landuse[l] is LandUse.UNPAVED_ROAD:
            z.n2d = z.AvLuSedYield[l]
            z.n6d = z.AvLuTotNitr[l]
            z.n13d = z.AvLuTotPhos[l]
            z.n6ddn = z.AvLuDisNitr[l]
            z.n13ddp = z.AvLuDisPhos[l]
        else:
            AvOtherLuSed = AvOtherLuSed + z.AvLuSedYield[l]
            # AvOtherLuNitr = AvOtherLuNitr + z.AvLuTotNitr[l]
            AvOtherLuPhos = AvOtherLuPhos + z.AvLuTotPhos[l]

    z.n2c = 0
    z.n6c = 0
    z.n13c = 0
    z.n24b = 0
    z.n2b = 0
    z.n6b = 0
    z.n13b = 0
    z.n23b = 0
    z.n6cdn = 0
    z.n13cdp = 0
    z.n6bdn = 0
    z.n13bdp = 0

    for l in range(z.NRur, z.NLU):
        if z.Landuse[l] in [LandUse.LD_MIXED, LandUse.LD_RESIDENTIAL]:
            z.n2c = z.n2c + z.AvLuSedYield[l]
            z.n6c = z.n6c + z.AvLuTotNitr[l]
            z.n13c = z.n13c + z.AvLuTotPhos[l]
            z.n6cdn = z.n6cdn + z.AvLuDisNitr[l]
            z.n13cdp = z.n13cdp + z.AvLuDisPhos[l]
            z.n24b = z.n24b + round(z.Area[l])
        elif z.Landuse[l] in [LandUse.MD_MIXED, LandUse.HD_MIXED,
                              LandUse.MD_RESIDENTIAL, LandUse.HD_RESIDENTIAL]:
            z.n2b = z.n2b + z.AvLuSedYield[l]
            z.n6b = z.n6b + z.AvLuTotNitr[l]
            z.n13b = z.n13b + z.AvLuTotPhos[l]
            z.n6bdn = z.n6bdn + z.AvLuDisNitr[l]
            z.n13bdp = z.n13bdp + z.AvLuDisPhos[l]
            z.n23b = z.n23b + round(z.Area[l])

    # Initial Upland loads
    # InitialUplandN = z.n5 + z.n6 + z.n6b + z.n6c + z.n6d + AvOtherLuNitr
    # if InitialUplandN == 0:
    #     InitialUplandN = 0.00000000001  # Fix for Divide-by-Zero error
    # InitialUplandP = z.n12 + z.n13 + z.n13b + z.n13c + z.n13d + AvOtherLuPhos
    # if InitialUplandP == 0:
    #     InitialUplandP = 0.00000000001  # Fix for Divide-by-Zero error
    # InitialUplandSed = z.n1 + z.n2 + z.n2b + z.n2c + z.n2d + AvOtherLuSed
    # if InitialUplandSed == 0:
    #     InitialUplandSed = 0.00000000001  # Fix for Divide-by-Zero error

    # FOR POINT SOURCE
    YrPointNitr = 0
    YrPointPhos = 0
    for i in range(0, 12):
        YrPointNitr = YrPointNitr + z.PointNitr[i]
        YrPointPhos = YrPointPhos + z.PointPhos[i]

    # GET THE AVERAGE SEPTIC SYSTEM INFORMATION
    if z.SepticFlag is YesOrNo.YES:
        for i in range(12):
            TotSewerSys = TotSewerSys + z.NumSewerSys[i]
            TotNormSys = TotNormSys + z.NumNormalSys[i]
            TotShortSys = TotShortSys + z.NumShortSys[i]
            TotSeptSys = (TotSeptSys + z.NumNormalSys[i] + z.NumShortSys[i] +
                          z.NumPondSys[i] + z.NumDischargeSys[i])

    # Set the conversion factors from metric to english
    SedConvert = 1000
    SedConvert = 1
    # NPConvert = 1

    # Get the animal nuntient loads
    # z.GRLBN = z.AvGRLostBarnNSum
    # z.NGLBN = z.AvNGLostBarnNSum
    z.GRLBP = z.AvGRLostBarnPSum
    z.NGLBP = z.AvNGLostBarnPSum
    z.NGLManP = z.AvNGLostManPSum

    # Get the fecal coliform values
    z.NGLBFC = z.AvNGLostBarnFCSum
    z.GRLBFC = z.AvGRLostBarnFCSum
    z.GRSFC = z.AvGRStreamFC
    # z.GRSN = z.AvGRStreamN
    z.GRSP = z.AvGRStreamP

    # Get the initial pathogen loads
    z.n139 = z.AvAnimalFCSum
    z.n140 = z.AvWWOrgsSum
    z.n146 = z.AvWWOrgsSum
    z.n141 = z.AvSSOrgsSum
    z.n147 = z.AvSSOrgsSum
    z.n142 = z.AvUrbOrgsSum
    z.n143 = z.AvWildOrgsSum
    z.n149 = z.AvWildOrgsSum

    # FARM ANIMAL LOADS
    # z.n7b_2 = z.AvAnimalNSum
    z.n14b = z.AvAnimalPSum

    # XXX: These are not used in our port.
    # InitialAnimalN = z.n7b
    # InitialAnimalP = z.n14b

    # Get the AEUs
    z.n41j = round(TotLAEU(z.NumAnimals, z.AvgAnimalWt))
    z.n41k = round(TotPAEU_2(z.NumAnimals, z.AvgAnimalWt))
    z.n41l = round(TotAEU_2(z.NumAnimals, z.AvgAnimalWt))

    # CONVERT AVERAGE STREAM BANK ERIOSION, N AND P TO ENGLISH UNITS
    z.n4 = round(z.AvStreamBankErosSum * z.RetentFactorSed * (1 - z.AttenTSS) * SedConvert)
    z.n8 = round(AvStreamBankNSum_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                                    z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                    z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                    z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                    z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                                    z.StreamWithdrawal,
                                    z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0,
                                    z.AvKF, z.AvSlope,
                                    z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n54,
                                    z.n85,
                                    z.UrbBankStab, z.SedNitr,
                                    z.BankNFrac, z.n69c, z.n45, z.n69) * NPConvert * RetentFactorN(z.ShedAreaDrainLake,
                                                                                                   z.RetentNLake) * (
                         1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)))
    z.n15 = round(z.AvStreamBankPSum * NPConvert * z.RetentFactorP * (1 - z.AttenP))

    # PERFORM LOAD REDUCTIONS BASED ON BMPS IN SCENARIO FILE
    AdjustScnLoads(z)

    # CONVERT AVERAGE STREAM BANK ERIOSION, N AND P TO ENGLISH UNITS
    z.AvStreamBankErosSum = z.n4
    z.AvStreamBankNSum = z.n8
    z.AvStreamBankPSum = z.n15

    z.AvAnimalFCSum = z.n145
    z.AvUrbOrgsSum = z.n148

    # Get the FC reduction for monthly loads
    UrbanFCFrac = 0
    FarmFCFrac = 0

    if z.n139 > 0:
        FarmFCFrac = z.n145 / z.n139
    if z.n142 > 0:
        UrbanFCFrac = z.n148 / z.n142

    for i in range(12):
        z.AvAnimalFC[i] = z.AvAnimalFC[i] * FarmFCFrac
        z.AvUrbOrgs[i] = z.AvUrbOrgs[i] * UrbanFCFrac

    # Reset the existing urban and animal FC loads to the reduced future loads, n145 and n148
    z.n139 = z.n145
    z.n142 = z.n148

    # Initial pathogen total load
    z.n144 = z.n139 + z.n140 + z.n141 + z.n142 + z.n143

    # Reduced total pathogen loads
    z.n150 = z.n145 + z.n146 + z.n147 + z.n148 + z.n149
    z.AvTotalOrgsSum = z.n150

    # FARM ANIMAL LOAD REDUCTION FOR N AND P
    # z.AvAnimalNSum_1 = z.n7b
    z.AvAnimalPSum = z.n14b
    # z.n7b_1 = z.n7b * NPConvert
    z.n14b = z.n14b * NPConvert

    # XXX: These are not used in our port
    # FinalAnimalN = z.n7b
    # FinalAnimalP = z.n14b

    # z.GRLBN = z.GRLBN * NPConvert #not used
    # z.NGLBN = z.NGLBN * NPConvert
    z.GRLBP = z.GRLBP * NPConvert
    z.NGLBP = z.NGLBP * NPConvert
    z.NGLManP = z.NGLManP * NPConvert
    # z.GRSN_2 = z.AvGRStreamN * NPConvert
    z.GRSP = z.AvGRStreamP * NPConvert

    # RESET GWLF OUTPUT VALUES FOR RURAL LANDUSE TO REDUCED LOADS AND CONVERT SCENARIO VALUES
    for l in range(z.NLU):
        if z.Landuse[l] is LandUse.HAY_PAST:
            z.AvLuSedYield[l] = z.n2
            z.AvLuTotNitr[l] = z.n6
            z.AvLuTotPhos[l] = z.n13
            z.AvLuDisNitr[l] = z.n6dn
            z.AvLuDisPhos[l] = z.n13dp

            if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
                z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
            if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
                z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

            z.n2 = round(z.AvLuSedYield[l] * SedConvert)
            z.n6 = round(z.AvLuTotNitr[l] * NPConvert)
            z.n13 = round(z.AvLuTotPhos[l] * NPConvert)

            if z.Area[l] > 0:
                AreaSum[2] = AreaSum[2] + z.Area[l]
        elif z.Landuse[l] is LandUse.CROPLAND:
            z.AvLuSedYield[l] = z.n1
            z.AvLuTotNitr[l] = z.n5
            z.AvLuTotPhos[l] = z.n12
            z.AvLuDisNitr[l] = z.n5dn
            z.AvLuDisPhos[l] = z.n12dp

            if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
                z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
            if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
                z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

            z.n1 = round(z.AvLuSedYield[l] * SedConvert)
            z.n5 = round(z.AvLuTotNitr[l] * NPConvert)
            z.n12 = round(z.AvLuTotPhos[l] * NPConvert)

            if z.Area[l] > 0:
                AreaSum[3] = AreaSum[3] + z.Area[l]
        elif z.Landuse[l] is LandUse.UNPAVED_ROAD:
            z.AvLuSedYield[l] = z.n2d
            z.AvLuTotNitr[l] = z.n6d
            z.AvLuTotPhos[l] = z.n13d
            z.AvLuDisNitr[l] = z.n6ddn
            z.AvLuDisPhos[l] = z.n13ddp

            if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
                z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
            if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
                z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

            z.n2d = round(z.AvLuSedYield[l] * SedConvert)
            z.n6d = round(z.AvLuTotNitr[l] * NPConvert)
            z.n13d = round(z.AvLuTotPhos[l] * NPConvert)

            if z.Area[l] > 0:
                AreaSum[6] = AreaSum[6] + z.Area[l]

        if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
            z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
        if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
            z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

        # GET THE AVERAGE TOTAL LOADS BY SOURCE
        TotAvLuErosion = TotAvLuErosion + z.AvLuErosion[l]
        AvTotalSed = AvTotalSed + z.AvLuSedYield[l]
        AvDisN = AvDisN + z.AvLuDisNitr[l]
        AvTotalN = AvTotalN + z.AvLuTotNitr[l]
        AvDisP = AvDisP + z.AvLuDisPhos[l]
        AvTotalP = AvTotalP + z.AvLuTotPhos[l]

    # Reset the urban landuse values
    for l in range(z.NRur, z.NLU):
        if z.n24b > 0 and z.Landuse[l] in [LandUse.LD_MIXED, LandUse.LD_RESIDENTIAL]:
            z.AvLuSedYield[l] = z.n2c * z.Area[l] / z.n24b
            z.AvLuTotNitr[l] = z.n6c * z.Area[l] / z.n24b
            z.AvLuTotPhos[l] = z.n13c * z.Area[l] / z.n24b
            z.AvLuDisNitr[l] = z.n6cdn * z.Area[l] / z.n24b
            z.AvLuDisPhos[l] = z.n13cdp * z.Area[l] / z.n24b

            if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
                z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
            if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
                z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

            if z.Area[l] > 0:
                AreaSum[0] = AreaSum[0] + z.Area[l]
        elif z.n23b > 0 and z.Landuse[l] in [LandUse.MD_MIXED, LandUse.HD_MIXED,
                                             LandUse.MD_RESIDENTIAL, LandUse.HD_RESIDENTIAL]:
            z.AvLuSedYield[l] = z.n2b * z.Area[l] / z.n23b
            z.AvLuTotNitr[l] = z.n6b * z.Area[l] / z.n23b
            z.AvLuTotPhos[l] = z.n13b * z.Area[l] / z.n23b
            z.AvLuDisNitr[l] = z.n6bdn * z.Area[l] / z.n23b
            z.AvLuDisPhos[l] = z.n13bdp * z.Area[l] / z.n23b

            if z.AvLuDisNitr[l] > z.AvLuTotNitr[l]:
                z.AvLuDisNitr[l] = z.AvLuTotNitr[l]
            if z.AvLuDisPhos[l] > z.AvLuTotPhos[l]:
                z.AvLuDisPhos[l] = z.AvLuTotPhos[l]

            if z.Area[l] > 0:
                AreaSum[1] = AreaSum[1] + z.Area[l]

    z.n2c = round(z.n2c * SedConvert)
    z.n6c = round(z.n6c * NPConvert)
    z.n13c = round(z.n13c * NPConvert)

    z.n2b = round(z.n2b * SedConvert)
    z.n6b = round(z.n6b * NPConvert)
    z.n13b = round(z.n13b * NPConvert)

    # XXX: These are not used in our port
    # Final Upland loads
    # FinalUplandN = z.n5 + z.n6 + z.n6b + z.n6c + z.n6d + AvOtherLuNitr
    # FinalUplandP = z.n12 + z.n13 + z.n13b + z.n13c + z.n13d + AvOtherLuPhos
    # FinalUplandSed = z.n1 + z.n2 + z.n2b + z.n2c + z.n2d + AvOtherLuSed

    # TotalAreaAc = 0

    # FORMAT VALUES FOR PREDICT SCENARIO FILE
    z.n22 = round(AreaTotal_2(z.Area), 0)

    # COMPLETE CALCULATING THE TOTAL SOURCE LOADS FOR SEDIMENT, N AND P
    AvTotalSed = (AvTotalSed + (((z.AvStreamBankErosSum / 1000) +
                  ((z.AvTileDrainSedSum / 1000)) * z.RetentFactorSed * (1 - z.AttenTSS))))
    AvDisN = (AvDisN + ((z.AvGroundNitrSum + YrPointNitr + z.AvSeptNitr) *
                        RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
    # AvTotalN = (AvTotalN + ((z.AvStreamBankNSum + (z.AvGroundNitrSum + z.AvTileDrainNSum +
    #             z.AvAnimalNSum + YrPointNitr + z.AvSeptNitr) * z.RetentFactorN * (1 - z.AttenN))))
    AvDisP = AvDisP + ((z.AvGroundPhosSum + YrPointPhos + z.AvSeptPhos) * z.RetentFactorP * (1 - z.AttenP))
    AvTotalP = (AvTotalP + ((z.AvStreamBankPSum + (z.AvGroundPhosSum + z.AvTileDrainPSum +
                                                   z.AvAnimalPSum + YrPointPhos + z.AvSeptPhos) * z.RetentFactorP * (
                                     1 - z.AttenP))))

    # OBTAIN THE AVERAGE TOTAL MONTHLY LOADS
    AvMonDisN = 0
    AvMonTotN = 0
    AvMonDisP = 0
    AvMonTotP = 0
    AvMonSed = 0
    AvMonEros = 0

    for i in range(12):
        AvMonEros = AvMonEros + \
                    AvErosion_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0, z.AntMoist_0,
                                  z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                  z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                                  z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0,
                                  z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab,
                                  z.SedDelivRatio_0, z.Acoef, z.KF, z.LS, z.C, z.P)[i]
        AvMonSed = AvMonSed + (
                AvSedYield_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                             z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                             z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                             z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                             z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt,
                             z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength,
                             z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab, z.Acoef, z.KF,
                             z.LS, z.C, z.P, z.SedDelivRatio_0) * z.RetentFactorSed * (1 - z.AttenTSS))
        AvMonDisN = AvMonDisN + (z.AvDisNitr[i] * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)))
        AvMonTotN = AvMonTotN + (z.AvTotNitr[i] * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)))
        AvMonDisP = AvMonDisP + (z.AvDisPhos[i] * z.RetentFactorP * (1 - z.AttenP))
        AvMonTotP = AvMonTotP + (z.AvTotPhos[i] * z.RetentFactorP * (1 - z.AttenP))

    # XXX: These values are not used in our port
    # Obtain the reduction factor to adjust the monthly loads if Scenario reductions applied
    # AvErosFrac = 1
    # AvSedFrac = 1
    # AvTotNFrac = 1
    # AvTotPFrac = 1
    # AvDisNFrac = 1
    # AvDisPFrac = 1

    # if AvMonEros > 0:
    #    AvErosFrac = TotAvLuErosion / AvMonEros
    # else:
    #    AvErosFrac = 0
    # if AvMonSed > 0:
    #    AvSedFrac = AvTotalSed / AvMonSed
    # else:
    #    AvSedFrac = 0
    # if AvMonDisN > 0:
    #    AvDisNFrac = AvDisN / AvMonDisN
    # else:
    #    AvDisNFrac = 0
    # if AvMonTotN > 0:
    #    AvTotNFrac = AvTotalN / AvMonTotN
    # else:
    #    AvTotNFrac = 0
    # if AvMonDisP > 0:
    #    AvDisPFrac = AvDisP / AvMonDisP
    # else:
    #    AvDisPFrac = 0
    # if AvMonTotP > 0:
    #    AvTotPFrac = AvTotalP / AvMonTotP
    # else:
    #    AvTotPFrac = 0

    # OBTAIN THE MONTHLY SEPTIC SYSTEM AND SEWER POPULATION VALUES
    z.n47 = round(TotSeptSys / 12)
    z.n49 = round(TotSeptSys / 12)
    z.n53 = round(TotSewerSys / 12)

    # CONVERT GROUNDWATER N AND P REDUCED LOADS INTO ENGLISH UNIST FOR THE PREDICT SCENARIO FILE
    z.n9 = round(((z.AvGroundNitrSum + z.AvTileDrainNSum) * NPConvert * RetentFactorN(z.ShedAreaDrainLake,
                                                                                      z.RetentNLake) * (
                          1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
    z.n16 = round(((z.AvGroundPhosSum + z.AvTileDrainPSum) * NPConvert * z.RetentFactorP * (1 - z.AttenP)))

    # CONVERT ANNUAL POINT N AND P TO ENGLISH UNITS
    z.n10 = round((YrPointNitr * NPConvert * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
            1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
    z.n17 = round((YrPointPhos * NPConvert * z.RetentFactorP * (1 - z.AttenP)))

    # CONVERT AVERAGE SEPTIC N AND P TO ENGLISH UNITS
    z.n11 = round((z.AvSeptNitr * NPConvert * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
            1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
    z.n18 = round((z.AvSeptPhos * NPConvert * z.RetentFactorP * (1 - z.AttenP)))

    # ENTER THE OTHER SEDIMENT, N AND P INTO FIELDS
    z.n3 = round(((AvOtherLuSed + ((z.AvTileDrainSedSum * z.RetentFactorSed * (1 - z.AttenTSS)) / 1000)) * SedConvert))
    # z.n7 = round((AvOtherLuNitr * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
    #         1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)) * NPConvert))
    z.n14 = round((AvOtherLuPhos * z.RetentFactorP * (1 - z.AttenP) * NPConvert))

    # ADD TURF TO HAY/PASTURE
    z.n2 = z.n2 + (n2t * SedConvert)
    z.n6 = z.n6 + (n6t * NPConvert)
    z.n13 = z.n13 + (n13t * NPConvert)
    z.n24 = z.n24 + n24t

    # Multiply sediment loads by 1000 to get them into Kg before writing to PRedICT section of file
    z.n1 = z.n1 * 1000
    z.n2 = z.n2 * 1000
    z.n2b = z.n2b * 1000
    z.n2c = z.n2c * 1000
    z.n2d = z.n2d * 1000
    z.n3 = z.n3 * 1000

    # Obtain the totals for sed, z.n az.nd P
    # Obtain the totals for sed, N and P
    z.n19 = z.n1 + z.n2 + z.n2b + z.n2c + z.n2d + z.n3 + z.n4
    # z.n20 = z.n5 + z.n6 + z.n6b + z.n6c + z.n6d + z.n7 + z.n7b + z.n8 + z.n9 + z.n10 + z.n11
    z.n21 = z.n12 + z.n13 + z.n13b + z.n13c + z.n13d + z.n14 + z.n14b + z.n15 + z.n16 + z.n17 + z.n18

    # TODO: Port WriteDailyFlowFile if needed
    # WRITE OUTPUT TO THE FILE FOR DAILy Flow
    # WriteDailyFlowFile

    # SET THE SCENARIO VALUES TO LANDUSE LOADS\
    AvOtherLuSed = 0
    # AvOtherLuNitr = 0
    AvOtherLuPhos = 0

    lu_tot_nitr_1 = LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                  z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                  z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                  z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                  z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)

    for y in range(z.NYrs):
        z.n2c = 0
        z.n6c = 0
        z.n13c = 0
        z.n2b = 0
        z.n6b = 0
        z.n13b = 0
        z.n6cdn = 0
        z.n13cdp = 0
        z.n6bdn = 0
        z.n13bdp = 0

        for l in range(z.NLU):
            # z.LuRunoff[y][l] = round(LuRunoff(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.NRur, z.NUrb, z.CNI_0, z.CNP_0,
            #                     z.AntMoist_0, z.Grow_0, z.Imper, z.ISRR, z.ISRA, z.CN)[y][l])
            # z.LuErosion_1[y][l] = round(z.LuErosion[y][l])
            z.LuSedYield[y][l] = round((z.LuSedYield[y][l] * z.RetentFactorSed * (1 - z.AttenTSS)))
            z.LuDisNitr[y][l] = round((z.LuDisNitr[y][l] * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                    1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
            # z.LuTotNitr_1[y][l] = round((z.LuTotNitr[y][l] * z.RetentFactorN * (1 - z.AttenN)))
            z.LuDisPhos[y][l] = round((z.LuDisPhos[y][l] * z.RetentFactorP * (1 - z.AttenP)))
            z.LuTotPhos_1[y][l] = round((z.LuTotPhos[y][l] * z.RetentFactorP * (1 - z.AttenP)))

            if z.Landuse[l] is LandUse.HAY_PAST:
                z.n2 = z.LuSedYield[y][l]
                z.n6 = LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                     z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                     z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                     z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                     z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n13 = z.LuTotPhos_1[y][l]
                z.n6dn = z.LuDisNitr[y][l]
                z.n13dp = z.LuDisPhos[y][l]
            elif z.Landuse[l] is LandUse.CROPLAND:
                z.n1 = z.LuSedYield[y][l]
                z.n5 = LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                     z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                     z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                     z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                     z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n12 = z.LuTotPhos_1[y][l]
                z.n5dn = z.LuDisNitr[y][l]
                z.n12dp = z.LuDisPhos[y][l]
            elif z.Landuse[l] is LandUse.UNPAVED_ROAD:
                z.n2d = z.LuSedYield[y][l]
                z.n6d = LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                      z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                      z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                      z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                      z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n13d = z.LuTotPhos_1[y][l]
                z.n6ddn = z.LuDisNitr[y][l]
                z.n13ddp = z.LuDisPhos[y][l]
            elif z.Landuse[l] is LandUse.TURFGRASS:
                z.n2t = z.LuSedYield[y][l]
                z.n6t = LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                      z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                      z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                      z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                      z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n13t = z.LuTotPhos_1[y][l]
            else:
                AvOtherLuSed = AvOtherLuSed + z.LuSedYield[y][l]
                # AvOtherLuNitr = AvOtherLuNitr + \
                #                 LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur,
                #                               z.NUrb, z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas,
                #                               z.FirstManureMonth, z.LastManureMonth, z.FirstManureMonth2,
                #                               z.LastManureMonth2, z.SedDelivRatio_0, z.KF, z.LS, z.C, z.P, z.SedNitr,
                #                               z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                #                               z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                AvOtherLuPhos = AvOtherLuPhos + z.LuTotPhos_1[y][l]

            if z.Landuse[l] in [LandUse.LD_MIXED, LandUse.LD_RESIDENTIAL]:
                z.n2c = z.n2c + z.LuSedYield[y][l]
                z.n6c = z.n6c + \
                        LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                      z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                      z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                      z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                      z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n13c = z.n13c + z.LuTotPhos_1[y][l]
                z.n6cdn = z.n6cdn + z.LuDisNitr[y][l]
                z.n13cdp = z.n13cdp + z.LuDisPhos[y][l]
            elif z.Landuse[l] in [LandUse.MD_MIXED, LandUse.HD_MIXED,
                                  LandUse.MD_RESIDENTIAL, LandUse.HD_RESIDENTIAL]:
                z.n2b = z.n2b + z.LuSedYield[y][l]
                z.n6b = z.n6b + \
                        LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                                      z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                                      z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                                      z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                                      z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y][l]
                z.n13b = z.n13b + z.LuTotPhos_1[y][l]
                z.n6bdn = z.n6bdn + z.LuDisNitr[y][l]
                z.n13bdp = z.n13bdp + z.LuDisPhos[y][l]

        # Convert animal loads into English units
        # z.GRLBN = z.GRLostBarnNSum[y] #not used
        # z.NGLBN = z.NGLostBarnNSum[y]
        z.GRLBP = z.GRLostBarnPSum[y]
        z.NGLBP = z.NGLostBarnPSum[y]
        z.NGLManP = z.NGLostManPSum[y]

        # Get the fecal coliform values
        z.NGLBFC = z.NGLostBarnFCSum[y]
        z.GRLBFC = z.GRLostBarnFCSum[y]
        z.GRSFC = z.AvGRStreamFC
        # z.GRSN_3 = z.AvGRStreamN
        z.GRSP = z.AvGRStreamP

        # Get the initial pathogen loads
        z.n139 = z.AnimalFCSum[y]
        z.n140 = z.WWOrgsSum[y]
        z.n146 = z.WWOrgsSum[y]
        z.n141 = z.SSOrgsSum[y]
        z.n147 = z.SSOrgsSum[y]
        z.n142 = z.UrbOrgsSum[y]
        z.n143 = z.WildOrgsSum[y]
        z.n149 = z.WildOrgsSum[y]

        # Initial pathogen total load
        z.n144 = z.n139 + z.n140 + z.n141 + z.n142 + z.n143

        # FARM ANIMAL LOADS
        n7b = z.AnimalNSum[y]
        # BUG: This is a bug in the original code.
        # This should be AnimalPSum
        n14b = z.AnimalNSum[y]

        # CONVERT AVERAGE STREAM BANK ERIOSION, N AND P TO ENGLISH UNITS
        z.n4 = round((z.StreamBankErosSum[y] * z.RetentFactorSed * (1 - z.AttenTSS) * SedConvert))
        z.n8 = round((StreamBankNSum_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                       z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN,
                                       z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0,
                                       z.RecessionCoef, z.SeepCoef, z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse,
                                       z.TileDrainDensity, z.PointFlow, z.StreamWithdrawal, z.GroundWithdrawal,
                                       z.NumAnimals, z.AvgAnimalWt, z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF,
                                       z.AvSlope, z.SedAAdjust, z.StreamLength, z.n42b, z.AgLength,
                                       z.UrbBankStab, z.SedNitr, z.BankNFrac, z.n69c, z.n45, z.n69)[
                          y] * NPConvert * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                              1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))))
        z.n15 = round((z.StreamBankPSum[y] * NPConvert * z.RetentFactorP * (1 - z.AttenP)))

        # PERFORM LOAD REDUCTIONS BASED ON BMPS IN SCENARIO FILE
        AdjustScnLoads(z)

        # CONVERT AVERAGE STREAM BANK ERIOSION, N AND P TO ENGLISH UNITS
        z.StreamBankErosSum[y] = z.n4
        # z.StreamBankNSum[y] = z.n8
        z.StreamBankPSum[y] = z.n15

        z.AnimalFCSum[y] = z.n145
        z.UrbOrgsSum[y] = z.n148

        # Get the FC reduction for monthly loads
        UrbanFCFrac = 0
        FarmFCFrac = 0

        if z.n139 > 0:
            FarmFCFrac = z.n145 / z.n139
        if z.n142 > 0:
            UrbanFCFrac = z.n148 / z.n142

        for i in range(12):
            z.AnimalFCSum[y] *= FarmFCFrac
            z.UrbOrgsSum[y] *= UrbanFCFrac

        # Reduced total pathogen loads
        n150 = z.n145 + z.n146 + z.n147 + z.n148 + z.n149
        z.TotalOrgsSum[y] = n150

        # FARM ANIMAL LOADS
        z.AnimalNSum[y] = n7b
        # BUG: This is a bug in the original code.
        # This should be AnimalPSum
        z.AnimalNSum[y] = n14b

        # FOR ALL LAND USES
        z.TotDisNitr = 0
        z.TotTotNitr = 0
        z.TotDisPhos = 0
        z.TotTotPhos = 0
        z.TotSedyield = 0
        z.LuTotNitr_2[y] = \
            LuTotNitr_1_2(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec, z.AntMoist_0, z.NRur, z.NUrb,
                          z.CN, z.Grow_0, z.Area, z.NitrConc, z.ManNitr, z.ManuredAreas, z.FirstManureMonth,
                          z.LastManureMonth, z.FirstManureMonth2, z.LastManureMonth2, z.SedDelivRatio_0,
                          z.KF, z.LS, z.C, z.P, z.SedNitr, z.Acoef, z.ShedAreaDrainLake, z.RetentNLake,
                          z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)[y]
        for l in range(z.NLU):
            if z.Landuse[l] is LandUse.HAY_PAST:
                z.LuSedYield[y][l] = z.n2
                z.LuTotNitr_2[y][l] = z.n6
                z.LuTotPhos_1[y][l] = z.n13
                z.LuDisNitr[y][l] = z.n6dn
                z.LuDisPhos[y][l] = z.n13dp

                if z.LuDisNitr[y][l] > z.LuTotNitr_2[y][l]:
                    z.LuDisNitr[y][l] = z.LuTotNitr_2[y][l]
                if z.LuDisPhos[y][l] > z.LuTotPhos_1[y][l]:
                    z.LuDisPhos[y][l] = z.LuTotPhos_1[y][l]
            elif z.Landuse[l] is LandUse.CROPLAND:
                if z.LuDisNitr[y][l] > 0:
                    z.LuDisNitr[y][l] = z.LuDisNitr[y][l] * z.n5 / z.LuTotNitr_2[y][l]
                if z.LuDisPhos[y][l] > 0:
                    z.LuDisPhos[y][l] = z.LuDisPhos[y][l] * z.n12 / z.LuTotPhos_1[y][l]

                z.LuSedYield[y][l] = z.n1
                z.LuTotNitr_2[y][l] = z.n5
                z.LuTotPhos_1[y][l] = z.n12
                z.LuDisNitr[y][l] = z.n5dn
                z.LuDisPhos[y][l] = z.n12dp
            elif z.Landuse[l] is LandUse.UNPAVED_ROAD:
                z.LuSedYield[y][l] = z.n2d
                z.LuTotNitr_2[y][l] = z.n6d
                z.LuTotPhos_1[y][l] = z.n13d
                z.LuDisNitr[y][l] = z.n6ddn
                z.LuDisPhos[y][l] = z.n13ddp

                if z.LuDisNitr[y][l] > z.LuTotNitr_2[y][l]:
                    z.LuDisNitr[y][l] = z.LuTotNitr_2[y][l]
                if z.LuDisPhos[y][l] > z.LuTotPhos_1[y][l]:
                    z.LuDisPhos[y][l] = z.LuTotPhos_1[y][l]

            if z.n24b > 0 and z.Landuse[l] in [LandUse.LD_MIXED, LandUse.LD_RESIDENTIAL]:
                z.LuSedYield[y][l] = z.n2c * z.Area[l] / z.n24b
                z.LuTotNitr_2[y][l] = z.n6c * z.Area[l] / z.n24b
                z.LuTotPhos_1[y][l] = z.n13c * z.Area[l] / z.n24b
                z.LuDisNitr[y][l] = z.n6cdn * z.Area[l] / z.n24b
                z.LuDisPhos[y][l] = z.n13cdp * z.Area[l] / z.n24b

                if z.LuDisNitr[y][l] > z.LuTotNitr_2[y][l]:
                    z.LuDisNitr[y][l] = z.LuTotNitr_2[y][l]
                if z.LuDisPhos[y][l] > z.LuTotPhos_1[y][l]:
                    z.LuDisPhos[y][l] = z.LuTotPhos_1[y][l]
            elif z.n23b > 0 and z.Landuse[l] in [LandUse.MD_MIXED, LandUse.HD_MIXED,
                                                 LandUse.MD_RESIDENTIAL, LandUse.HD_RESIDENTIAL]:
                z.LuSedYield[y][l] = z.n2b * z.Area[l] / z.n23b
                z.LuTotNitr_2[y][l] = z.n6b * z.Area[l] / z.n23b
                z.LuTotPhos_1[y][l] = z.n13b * z.Area[l] / z.n23b
                z.LuDisNitr[y][l] = z.n6bdn * z.Area[l] / z.n23b
                z.LuDisPhos[y][l] = z.n13bdp * z.Area[l] / z.n23b

                if z.LuDisNitr[y][l] > z.LuTotNitr_2[y][l]:
                    z.LuDisNitr[y][l] = z.LuTotNitr_2[y][l]
                if z.LuDisPhos[y][l] > z.LuTotPhos_1[y][l]:
                    z.LuDisPhos[y][l] = z.LuTotPhos_1[y][l]
            if z.LuDisNitr[y][l] > z.LuTotNitr_2[y][l]:
                z.LuDisNitr[y][l] = z.LuTotNitr_2[y][l]
            if z.LuDisPhos[y][l] > z.LuTotPhos_1[y][l]:
                z.LuDisPhos[y][l] = z.LuTotPhos_1[y][l]

    # WRITE THE RESULTS FILES INTO THE OUTPUT DIRECTORY IN METRIC UNITS
    # TODO: Skipping section that prepares and writes AnnualFile and AnnCsvFile
    # Lines ~630 - 921

    # WRITE THE SUMARY FILES TO THE OUTPUT DIRECTORY IN METRIC UNITS
    # TODO: For now, we are only writing the first chunk of AvgFile

    # Sum Variables for Aggregate Summary Ouput Files
    # if FirstRun: XXX: Commented out because we don't
    # have the concept of a "first run" in the port.
    SumNYrs = z.NYrs
    SumNRur = z.NRur
    SumNUrb = z.NUrb
    SumNLU = z.NLU
    # SumOpt = z.Opt
    SumWxYrBeg = z.WxYrBeg
    SumWxYrEnd = z.WxYrEnd

    if z.NYrs > SumNYrs:
        SumNYrs = z.NYrs
    if z.NRur > SumNRur:
        SumNRur = z.NRur
    if z.NUrb > SumNUrb:
        SumNUrb = z.NUrb
    if z.NLU > SumNLU:
        SumNLU = z.NLU
    # if z.Opt > SumOpt:
    #    SumOpt = z.Opt
    if z.WxYrBeg < SumWxYrBeg:
        SumWxYrBeg = z.WxYrBeg
    if z.WxYrEnd > SumWxYrEnd:
        SumWxYrEnd = z.WxYrEnd

    # Which land use sources to include in the totals.
    sources = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

    # ha
    AreaTotal = sum(z.Area[l] for l in sources)

    # kg
    SumSed = sum(z.AvLuSedYield[l] for l in sources) * TONNE_TO_KG
    SumSed += z.AvStreamBankErosSum

    # kg
    SumNitr = sum(z.AvLuTotNitr[l] for l in sources)
    SumNitr += z.AvStreamBankNSum
    SumNitr += AvAnimalNSum_1_2(z.NYrs, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN, z.NGAppNRate,
                              z.NGPctSoilIncRate, z.GRAppNRate, z.GRPctSoilIncRate, z.GrazingNRate, z.GRPctManApp,
                              z.PctGrazing, z.GRBarnNRate,
                              z.Prec, z.DaysMonth, z.AWMSGrPct, z.GrAWMSCoeffN, z.RunContPct, z.RunConCoeffN, z.n41b,
                              z.n85h, z.NGPctManApp, z.AWMSNgPct,
                              z.NGBarnNRate, z.NgAWMSCoeffN, z.n41d, z.n85j, z.n41f, z.n85l, z.PctStreams, z.n42, z.n45,
                              z.n69, z.n43, z.n64) * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))
    SumNitr += z.AvGroundNitrSum * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))
    SumNitr += YrPointNitr * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))
    SumNitr += z.AvSeptNitr * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN))

    # kg
    SumPhos = sum(z.AvLuTotPhos[l] for l in sources)
    SumPhos += z.AvStreamBankPSum
    SumPhos += z.AvAnimalPSum * z.RetentFactorP * (1 - z.AttenP)
    SumPhos += z.AvGroundPhosSum * z.RetentFactorP * (1 - z.AttenP)
    SumPhos += YrPointPhos * z.RetentFactorP * (1 - z.AttenP)
    SumPhos += z.AvSeptPhos * z.RetentFactorP * (1 - z.AttenP)

    # m^3/year
    MeanFlow = (z.AvStreamFlowSum * CM_TO_M) * (AreaTotal * HA_TO_M2)

    # Find index of month with lowest mean flow.
    LowFlowMonth = z.AvStreamFlow.tolist().index(min(z.AvStreamFlow))

    # m^3/year
    MeanLowFlow = (z.AvStreamFlow[LowFlowMonth] * CM_TO_M) * (AreaTotal * HA_TO_M2)

    # m^3/second
    MeanFlowPS = MeanFlow / 31536000

    # kg/ha
    if AreaTotal > 0:
        LoadingRateSed = SumSed / AreaTotal
        LoadingRateN = SumNitr / AreaTotal
        LoadingRateP = SumPhos / AreaTotal
    else:
        LoadingRateSed = 0
        LoadingRateN = 0
        LoadingRateP = 0

    # mg/l
    if MeanFlow > 0:
        ConcSed = (SumSed * KG_TO_MG) / (MeanFlow * M3_TO_L)
        ConcN = (SumNitr * KG_TO_MG) / (MeanFlow * M3_TO_L)
        ConcP = (SumPhos * KG_TO_MG) / (MeanFlow * M3_TO_L)
    else:
        ConcSed = 0
        ConcN = 0
        ConcP = 0

    # mg/l
    if MeanLowFlow > 0:
        LFConcSed = ((AvSedYield(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                                 z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                                 z.PcntET, z.DayHrs, z.MaxWaterCap, z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                 z.Qretention, z.PctAreaInfil, z.n25b, z.Landuse, z.TileDrainDensity, z.PointFlow,
                                 z.StreamWithdrawal, z.GroundWithdrawal, z.NumAnimals, z.AvgAnimalWt,
                                 z.StreamFlowVolAdj, z.SedAFactor_0, z.AvKF, z.AvSlope, z.SedAAdjust, z.StreamLength,
                                 z.n42b, z.n46c, z.n85d, z.AgLength, z.n42, z.n45, z.n85, z.UrbBankStab, z.Acoef, z.KF,
                                 z.LS, z.C, z.P, z.SedDelivRatio_0)[LowFlowMonth] * TONNE_TO_KG * KG_TO_MG) / (
                             MeanLowFlow * M3_TO_L))
        LFConcN = ((z.AvTotNitr[LowFlowMonth] * KG_TO_MG) /
                   (MeanLowFlow * M3_TO_L))
        LFConcP = ((z.AvTotPhos[LowFlowMonth] * KG_TO_MG) /
                   (MeanLowFlow * M3_TO_L))
    else:
        LFConcSed = 0
        LFConcN = 0
        LFConcP = 0

    output = {}

    # Equivalent to Line 927 of source
    output['meta'] = {
        'NYrs': z.NYrs,
        'NRur': z.NRur,
        'NUrb': z.NUrb,
        'NLU': z.NLU,
        'SedDelivRatio': SedDelivRatio(z.SedDelivRatio_0),
        'WxYrBeg': z.WxYrBeg,
        'WxYrEnd': z.WxYrEnd,
    }

    output['AreaTotal'] = AreaTotal
    output['MeanFlow'] = MeanFlow
    output['MeanFlowPerSecond'] = MeanFlowPS

    # Equivalent to lines 965 - 988 of source
    av_evapo_trans = AvEvapoTrans(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                                  z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV,
                                  z.PcntET, z.DayHrs,
                                  z.MaxWaterCap)  # TODO: once all of the monthly variables have been extracted, rewrite how this works
    av_tile_drain = AvTileDrain_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                  z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                  z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                  z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                  z.Landuse, z.TileDrainDensity)
    av_withdrawal = AvWithdrawal_2(z.NYrs, z.StreamWithdrawal, z.GroundWithdrawal)
    av_ground_water = AvGroundWater_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                      z.CNI_0,
                                      z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN, z.UnsatStor_0,
                                      z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                      z.SatStor_0, z.RecessionCoef, z.SeepCoef, z.Landuse, z.TileDrainDensity)
    av_runoff = AvRunoff_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                           z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.Qretention, z.PctAreaInfil,
                           z.n25b, z.CN, z.Landuse, z.TileDrainDensity)
    output['monthly'] = []
    for i in range(0, 12):
        output['monthly'].append({
            'AvPrecipitation': z.AvPrecipitation[i],
            'AvEvapoTrans': av_evapo_trans[i],
            'AvGroundWater': av_ground_water[i],
            'AvRunoff': av_runoff[i],
            'AvStreamFlow': z.AvStreamFlow[i],
            'AvPtSrcFlow': z.AvPtSrcFlow[i],
            'AvTileDrain': av_tile_drain[i],
            'AvWithdrawal': av_withdrawal[i],
        })

    output['Loads'] = []
    output['Loads'].append({
        'Source': 'Hay/Pasture',
        'Sediment': z.AvLuSedYield[0] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[0],
        'TotalP': z.AvLuTotPhos[0],
    })
    output['Loads'].append({
        'Source': 'Cropland',
        'Sediment': z.AvLuSedYield[1] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[1],
        'TotalP': z.AvLuTotPhos[1],
    })
    # Forest
    output['Loads'].append({
        'Source': 'Wooded Areas',
        'Sediment': z.AvLuSedYield[2] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[2],
        'TotalP': z.AvLuTotPhos[2],
    })
    output['Loads'].append({
        'Source': 'Wetlands',
        'Sediment': z.AvLuSedYield[3] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[3],
        'TotalP': z.AvLuTotPhos[3],
    })
    output['Loads'].append({
        'Source': 'Open Land',
        'Sediment': z.AvLuSedYield[6] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[6],
        'TotalP': z.AvLuTotPhos[6],
    })
    # Bare Rock, Sandy Areas
    output['Loads'].append({
        'Source': 'Barren Areas',
        'Sediment': sum(z.AvLuSedYield[l] * TONNE_TO_KG for l in (7, 8)),
        'TotalN': sum(z.AvLuTotNitr[l] for l in (7, 8)),
        'TotalP': sum(z.AvLuTotPhos[l] for l in (7, 8)),
    })
    output['Loads'].append({
        'Source': 'Low-Density Mixed',
        'Sediment': z.AvLuSedYield[10] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[10],
        'TotalP': z.AvLuTotPhos[10],
    })
    output['Loads'].append({
        'Source': 'Medium-Density Mixed',
        'Sediment': z.AvLuSedYield[11] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[11],
        'TotalP': z.AvLuTotPhos[11],
    })
    output['Loads'].append({
        'Source': 'High-Density Mixed',
        'Sediment': z.AvLuSedYield[12] * TONNE_TO_KG,
        'TotalN': z.AvLuTotNitr[12],
        'TotalP': z.AvLuTotPhos[12],
    })
    # Disturbed, Turfgrass, Unpaved Road
    output['Loads'].append({
        'Source': 'Other Upland Areas',
        'Sediment': sum(z.AvLuSedYield[l] * TONNE_TO_KG for l in (4, 5, 9)),
        'TotalN': sum(z.AvLuTotNitr[l] for l in (4, 5, 9)),
        'TotalP': sum(z.AvLuTotPhos[l] for l in (4, 5, 9)),
    })
    output['Loads'].append({
        'Source': 'Farm Animals',
        'Sediment': 0,
        'TotalN': AvAnimalNSum_1_2(z.NYrs, z.GrazingAnimal_0, z.NumAnimals, z.AvgAnimalWt, z.AnimalDailyN, z.NGAppNRate,
                                 z.NGPctSoilIncRate, z.GRAppNRate, z.GRPctSoilIncRate, z.GrazingNRate, z.GRPctManApp,
                                 z.PctGrazing, z.GRBarnNRate,
                                 z.Prec, z.DaysMonth, z.AWMSGrPct, z.GrAWMSCoeffN, z.RunContPct, z.RunConCoeffN, z.n41b,
                                 z.n85h, z.NGPctManApp, z.AWMSNgPct,
                                 z.NGBarnNRate, z.NgAWMSCoeffN, z.n41d, z.n85j, z.n41f, z.n85l, z.PctStreams, z.n42,
                                 z.n45, z.n69, z.n43, z.n64) * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (1 -  AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)),
        'TotalP': z.AvAnimalPSum * z.RetentFactorP * (1 - z.AttenP),
    })
    output['Loads'].append({
        'Source': 'Stream Bank Erosion',
        'Sediment': z.AvStreamBankErosSum,
        'TotalN': z.AvStreamBankNSum,
        'TotalP': z.AvStreamBankPSum,
    })
    output['Loads'].append({
        'Source': 'Subsurface Flow',
        'Sediment': 0,
        'TotalN': z.AvGroundNitrSum * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)),
        'TotalP': z.AvGroundPhosSum * z.RetentFactorP * (1 - z.AttenP),
    })
    output['Loads'].append({
        'Source': 'Point Sources',
        'Sediment': 0,
        'TotalN': YrPointNitr * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)),
        'TotalP': YrPointPhos * z.RetentFactorP * (1 - z.AttenP),
    })
    output['Loads'].append({
        'Source': 'Septic Systems',
        'Sediment': 0,
        'TotalN': z.AvSeptNitr * RetentFactorN(z.ShedAreaDrainLake, z.RetentNLake) * (
                1 - AttenN(z.AttenFlowDist, z.AttenFlowVel, z.AttenLossRateN)),
        'TotalP': z.AvSeptPhos * z.RetentFactorP * (1 - z.AttenP),
    })

    output['SummaryLoads'] = []
    output['SummaryLoads'].append({
        'Source': 'Total Loads',
        'Unit': 'kg',
        'Sediment': SumSed,
        'TotalN': SumNitr,
        'TotalP': SumPhos,
    })
    output['SummaryLoads'].append({
        'Source': 'Loading Rates',
        'Unit': 'kg/ha',
        'Sediment': LoadingRateSed,
        'TotalN': LoadingRateN,
        'TotalP': LoadingRateP,
    })
    output['SummaryLoads'].append({
        'Source': 'Mean Annual Concentration',
        'Unit': 'mg/l',
        'Sediment': ConcSed,
        'TotalN': ConcN,
        'TotalP': ConcP,
    })
    output['SummaryLoads'].append({
        'Source': 'Mean Low-Flow Concentration',
        'Unit': 'mg/l',
        'Sediment': LFConcSed,
        'TotalN': LFConcN,
        'TotalP': LFConcP,
    })

    return output


def WriteOutputSumFiles():
    pass


def UrbanAreasOutput():
    pass






def GRAccManAppN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing):
    result = np.zeros((12,))
    grazing_n = GrazingN(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    init_gr_n = InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = (result[i] + (init_gr_n / 12) - (GRPctManApp[i] * init_gr_n) - grazing_n[i])
        if result[i] < 0:
            result[i] = 0
    return result


def GRAccManAppN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing):
    init_gr_n = InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    grazing_n = GrazingN_2(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    return np.maximum(((1.0 / 12) - GRPctManApp) * init_gr_n - grazing_n, 0)

# @time_function
# def GRAccManAppN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing):
#     init_gr_n = InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
#     grazing_n = GrazingN_2(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
#     result = (np.repeat(init_gr_n / 12, 12)) - (GRPctManApp * np.repeat(init_gr_n, 12)) - grazing_n
#     result = np.maximum(result, 0)
#     return result



def GRAppManN(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((12,))
    init_gr_n = InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = GRPctManApp[i] * init_gr_n
    return result


def GRAppManN_2(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    init_gr_n = InitGrN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    return GRPctManApp * init_gr_n



def GrazingN(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((12,))
    init_gr_n = InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = PctGrazing[i] * (init_gr_n / 12)
    return result


def GrazingN_2(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    return (PctGrazing * (InitGrN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN) / 12))[None,:]



def GRInitBarnN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing):
    result = np.zeros((12,))
    gr_acc_man_app_n = GRAccManAppN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing)
    gr_app_man_n = GRAppManN(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = gr_acc_man_app_n[i] - gr_app_man_n[i]
    return result


def GRInitBarnN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing):
    return GRAccManAppN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                          PctGrazing) - GRAppManN_2(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)


def GRLoadN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((NAnimals,))
    grazing_animal = GrazingAnimal(GrazingAnimal_0)
    for a in range(9):
        if grazing_animal[a] is YesOrNo.NO:
            pass
        elif grazing_animal[a] is YesOrNo.YES:
            result[a] = (NumAnimals[a] * AvgAnimalWt[a] / 1000) * AnimalDailyN[a] * 365
    return result


def GRLoadN_2(GrazingAnimal_0,NumAnimals,AvgAnimalWt,AnimalDailyN):
    grazing_animals = GrazingAnimal_2(GrazingAnimal_0)
    return (NumAnimals[grazing_animals] * AvgAnimalWt[grazing_animals] / 1000) * AnimalDailyN[grazing_animals] * 365



def InitGrN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = 0
    gr_load_n = GRLoadN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    grazing_animal = GrazingAnimal(GrazingAnimal_0)
    for a in range(9):
        if grazing_animal[a] is YesOrNo.NO:
            pass
        elif grazing_animal[a] is YesOrNo.YES:
            result += gr_load_n[a]
    return result


def InitGrN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    return np.sum(GRLoadN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN))




def AvGRLostBarnN(NYrs, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((12,))
    gr_lost_barn_n = GRLostBarnN(NYrs, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                                 GRBarnNRate, Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += gr_lost_barn_n[Y][i] / NYrs
    return result


def AvGRLostBarnN_2(NYrs, Prec, DaysMonth, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                    PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    return np.average(
        GRLostBarnN_2(NYrs, Prec, DaysMonth, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                      PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN), axis=0)




def AvGRLostBarnNSum(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                     Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    av_gr_lost_barn_n = AvGRLostBarnN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                                      PctGrazing, GRBarnNRate, Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct,
                                      RunConCoeffN)
    result = sum(av_gr_lost_barn_n)
    return result


def AvGRLostBarnNSum_2(NYrs, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                       Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    return np.sum(AvGRLostBarnN_2(NYrs, Prec, DaysMonth, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                    PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN))


def GRLBN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                     Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    av_gr_lost_barn_n_sum = AvGRLostBarnNSum(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                     Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    result = av_gr_lost_barn_n_sum
    return result



def GRLBN_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                     Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    return AvGRLostBarnNSum_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                     Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)




def GRLossN(NYrs, PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GrazingNRate, Prec,
            DaysMonth):
    result = np.zeros((NYrs, 12))
    gr_stream_n = GRStreamN(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    grazing_n = GrazingN(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    loss_fact_adj = LossFactAdj(NYrs, Prec, DaysMonth)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = ((grazing_n[i] - gr_stream_n[i]) * GrazingNRate[i] * loss_fact_adj[Y][i])
            if result[Y][i] > (grazing_n[i] - gr_stream_n[i]):
                result[Y][i] = (grazing_n[i] - gr_stream_n[i])
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result


def GRLossN_2(NYrs, PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GrazingNRate, Prec,
              DaysMonth):
    grazing_n = np.reshape(
        np.repeat(GrazingN_2(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN), repeats=NYrs, axis=0),
        (NYrs, 12))
    gr_stream_n = np.reshape(
        np.repeat(GRStreamN_2(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN),
                  repeats=NYrs, axis=0),
        (NYrs, 12))
    loss_face_adj = LossFactAdj_2(Prec, DaysMonth)
    result = grazing_n - gr_stream_n
    adjusted = np.where(GrazingNRate * loss_face_adj < 1)
    result[adjusted] = result[adjusted] * (GrazingNRate * loss_face_adj)[adjusted]
    return result



def GRLostBarnN(NYrs, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((NYrs, 12))
    loss_fact_adj = LossFactAdj(NYrs, Prec, DaysMonth)
    gr_init_barn_n = GRInitBarnN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                                 PctGrazing)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (gr_init_barn_n[i] * GRBarnNRate[i] * loss_fact_adj[Y][i]
                            - gr_init_barn_n[i] * GRBarnNRate[i] * loss_fact_adj[Y][i] * AWMSGrPct * GrAWMSCoeffN
                            + gr_init_barn_n[i] * GRBarnNRate[i] * loss_fact_adj[Y][i] * RunContPct * RunConCoeffN)
            if result[Y][i] > gr_init_barn_n[i]:
                result[Y][i] = gr_init_barn_n[i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result


def GRLostBarnN_2(NYrs, Prec, DaysMonth, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp,
                  PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    loss_fact_adj = LossFactAdj_2(Prec, DaysMonth)
    gr_init_barn_n = GRInitBarnN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing)

    years_gr_init_barn_gr_barn_n_rate = np.resize(gr_init_barn_n * GRBarnNRate,
                                                  (NYrs, 12)) * loss_fact_adj  # TODO: what is a better name for this
    result = years_gr_init_barn_gr_barn_n_rate + \
             years_gr_init_barn_gr_barn_n_rate * (AWMSGrPct * GrAWMSCoeffN - RunContPct * RunConCoeffN)
    result = np.minimum(result, np.resize(gr_init_barn_n, (NYrs, 12)))
    result = np.maximum(result, 0)
    return np.reshape(result, (NYrs, 12))


def GRLostBarnNSum(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                   Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((NYrs, 12))
    gr_lost_barn_n = GRLostBarnN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                                 GRBarnNRate, Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y] += gr_lost_barn_n[Y][i]
    return result


def GRLostBarnNSum_2():
    pass




def GRLostManN(NYrs, GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRAppNRate, Prec, DaysMonth,
               GRPctSoilIncRate):
    result = np.zeros((NYrs, 12))
    loss_fact_adj = LossFactAdj(NYrs, Prec, DaysMonth)
    gr_app_man_n = GRAppManN(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (gr_app_man_n[i] * GRAppNRate[i] * loss_fact_adj[Y][i] * (1 - GRPctSoilIncRate[i]))
            if result[Y][i] > gr_app_man_n[i]:
                result[Y][i] = gr_app_man_n[i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result


def GRLostManN_2(NYrs, GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRAppNRate, Prec, DaysMonth,
                 GRPctSoilIncRate):
    lossFactAdj = LossFactAdj_2(Prec, DaysMonth)
    gr_app_man_n = GRAppManN_2(GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    result = (np.tile(gr_app_man_n, NYrs) * np.tile(GRAppNRate, NYrs) * np.ndarray.flatten(lossFactAdj) * np.tile(
        (1 - GRPctSoilIncRate), NYrs))
    result = np.minimum(result, np.tile(gr_app_man_n, NYrs))
    result = np.maximum(result, 0)
    return np.reshape(result, (NYrs, 12))

# import numpy as np
# from gwlfe.Timer import time_function
# from GRStreamN import AvGRStreamN
#this variable was just renaming AvGRStreamN, it is not needed
# def GRSN(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN):
#     av_gr_stream_n = AvGRStreamN(PctStreams,PctGrazing,GrazingAnimal,NumAnimals,AvgAnimalWt,AnimalDailyN)
#     return av_gr_stream_n
#
#
# def GRSN_2():
#     pass




def GRStreamN(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((12,))
    grazing_n = GrazingN(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = PctStreams[i] * grazing_n[i]
    return result


def GRStreamN_2(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    return PctStreams * GrazingN_2(PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)


def AvGRStreamN(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = 0
    gr_stream_n = GRStreamN(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result += gr_stream_n[i]
    return result


def AvGRStreamN_2(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN):
    return np.sum(GRStreamN_2(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN))





def InitNgN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = 0
    ng_load_n = NGLoadN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    grazing_animal = GrazingAnimal(GrazingAnimal_0)
    for a in range(9):
        if grazing_animal[a] is YesOrNo.NO:
            result += ng_load_n[a]
    return result


def InitNgN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    ng_load_n = NGLoadN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    return np.sum(ng_load_n)



def NGAccManAppN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGPctManApp):
    result = np.zeros((12,))
    init_ng_n = InitNgN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        # For Non-Grazing
        result[i] += (init_ng_n / 12) - (NGPctManApp[i] * init_ng_n)
        if result[i] < 0:
            result[i] = 0
    return result


def NGAccManAppN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGPctManApp):
    init_ng_n = InitNgN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    return np.maximum((init_ng_n / 12) - (NGPctManApp * init_ng_n),0)




def NGAppManN(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((12,))
    init_ng_n = InitNgN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for i in range(12):
        result[i] = NGPctManApp[i] * init_ng_n
    return result


def NGAppManN_2(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    return NGPctManApp * InitNgN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)




def NGInitBarnN(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((12,))
    ng_app_man_n = NGAppManN(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    ng_acc_man_app_n = NGAccManAppN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGPctManApp)
    for i in range(12):
        result[i] = ng_acc_man_app_n[i] - ng_app_man_n[i]
        if result[i] < 0:
            result[i] = 0
    return result


def NGInitBarnN_2(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    ng_app_man_n = NGAppManN_2(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    ng_acc_man_app_n = NGAccManAppN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGPctManApp)
    return np.maximum(ng_acc_man_app_n - ng_app_man_n, 0)[None,:]



def NGLoadN(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    result = np.zeros((9,))
    grazing_animal = GrazingAnimal(GrazingAnimal_0)
    for a in range(9):
        if grazing_animal[a] is YesOrNo.NO:
            result[a] = (NumAnimals[a] * AvgAnimalWt[a] / 1000) * AnimalDailyN[a] * 365
    return result


def NGLoadN_2(GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN):
    grazing_animal = GrazingAnimal_2(GrazingAnimal_0)
    grazing_mask = np.where(~grazing_animal)
    return (NumAnimals[grazing_mask] * AvgAnimalWt[grazing_mask] / 1000) * AnimalDailyN[grazing_mask] * 365



# The variable is just a renaming of AvNGLostBarnN, it is not needed
# def NGLBN(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
#                      Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
#     av_ng_lost_barn_n_sum = AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
#                      Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
#     result = av_ng_lost_barn_n_sum
#     return result


# def NGLBN_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
#                      Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
#     return AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
#                      Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)



def NGLostBarnN(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate, Prec,
                DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((NYrs, 12))
    loss_fact_adj = LossFactAdj(NYrs, Prec, DaysMonth)
    ng_init_barn_n = NGInitBarnN(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (ng_init_barn_n[i] * NGBarnNRate[i] * loss_fact_adj[Y][i]
                            - ng_init_barn_n[i] * NGBarnNRate[i] * loss_fact_adj[Y][i] * AWMSNgPct * NgAWMSCoeffN
                            + ng_init_barn_n[i] * NGBarnNRate[i] * loss_fact_adj[Y][i] * RunContPct * RunConCoeffN)
            if result[Y][i] > ng_init_barn_n[i]:
                result[Y][i] = ng_init_barn_n[i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result

def NGLostBarnN_2(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate, Prec,
                  DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    loss_fact_adj = LossFactAdj_2(Prec, DaysMonth)
    ng_init_barn_n = np.reshape(
        np.repeat(NGInitBarnN_2(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN), repeats=NYrs,
                  axis=0), (NYrs, 12))

    temp = NGBarnNRate * loss_fact_adj * (1 - AWMSNgPct * NgAWMSCoeffN + RunContPct * RunConCoeffN)
    # result would be less than the subexpression if the number that is subtracted is bigger than the one added
    adjusted = np.where(temp < 1)
    result = ng_init_barn_n
    result[adjusted] = ng_init_barn_n[adjusted] * temp[adjusted]
    return np.maximum(result, 0)

#TODO: this needs to be split into it's own function
def AvNGLostBarnN(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                  Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((12,))
    ng_lost_barn_n = NGLostBarnN(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                                 Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += ng_lost_barn_n[Y][i] / NYrs
    return result


def AvNGLostBarnN_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                  Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    return np.sum(NGLostBarnN_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                                 Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN),axis=0)/NYrs


def AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    av_ng_lost_barn_n = AvNGLostBarnN(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                      NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    result = sum(av_ng_lost_barn_n)
    return result


def AvNGLostBarnNSum_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    return np.sum(AvNGLostBarnN_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                      NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN))


def NGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate, Prec,
                   DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN):
    result = np.zeros((NYrs,))
    ng_lost_barn_n = NGLostBarnN(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                                 Prec,
                                 DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y] += ng_lost_barn_n[Y][i]
    return result


def NGLostBarnNSum_2():
    pass




def NGLostManN(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
               NGPctSoilIncRate):
    # Non-grazing animal losses
    result = np.zeros((NYrs, 12))
    loss_fact_adj = LossFactAdj(NYrs, Prec, DaysMonth)
    ng_app_man_n = NGAppManN(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (ng_app_man_n[i] * NGAppNRate[i] * loss_fact_adj[Y][i]
                            * (1 - NGPctSoilIncRate[i]))
            if result[Y][i] > ng_app_man_n[i]:
                result[Y][i] = ng_app_man_n[i]
            if result[Y][i] < 0:
                result[Y][i] = 0
    return result


def NGLostManN_2(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
                 NGPctSoilIncRate):
    lossFactAdj = LossFactAdj_2(Prec, DaysMonth)
    ng_app_man_n = NGAppManN_2(NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    result = np.tile(ng_app_man_n * NGAppNRate * (1 - NGPctSoilIncRate), NYrs) * np.ndarray.flatten(lossFactAdj)
    result = np.minimum(result, np.tile(ng_app_man_n, NYrs))  # TODO: should eliminate the double tile
    result = np.maximum(result, 0)
    return np.reshape(result, (NYrs, 12))





def NAGBUFFER(n42, n43, n64, NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
              Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, GRPctManApp, PctGrazing, GRBarnNRate,
              AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate, GRAppNRate, GRPctSoilIncRate,
              GrazingNRate):
    nglbn = AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    grlbn = GRLBN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    grsn = AvGRStreamN(PctStreams,PctGrazing,GrazingAnimal,NumAnimals,AvgAnimalWt,AnimalDailyN)
    av_animal_n_sum = AvAnimalNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate,
                                   Prec, DaysMonth, NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate,
                                   NGBarnNRate, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, PctGrazing,
                                   GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate)
    if n42 > 0:
        result = (n43 / n42) * n64 * (av_animal_n_sum - (nglbn + grlbn + grsn))
    else:
        result = 0
    return result


def NAGBUFFER_2(n42, n43, n64, NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
              Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, GRPctManApp, PctGrazing, GRBarnNRate,
              AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate, GRAppNRate, GRPctSoilIncRate,
              GrazingNRate):
    if n42 > 0:
        nglbn = AvNGLostBarnNSum_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                                 Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
        grlbn = GRLBN_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                      Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
        grsn = AvGRStreamN_2(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN)
        av_animal_n_sum = AvAnimalNSum_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate,
                                       Prec, DaysMonth, NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate,
                                       NGBarnNRate, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, PctGrazing,
                                       GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate)

        return (n43 / n42) * n64 * (av_animal_n_sum - (nglbn + grlbn + grsn))
    else:
        return 0



def NAWMSL(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
           Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h):
    grlbn = GRLBN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    result = (n41b / 100) * n85h * grlbn
    return result


def NAWMSL_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
           Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h):
    return (n41b/100) * n85h * GRLBN_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)


def NAWMSP(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
           Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j):
    nglbn = AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    result = (n41d / 100) * n85j * nglbn
    return result


def NAWMSP_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
           Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j):
    return (n41d / 100) * n85j * AvNGLostBarnNSum_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)


def NFENCING(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, n42, n45, n69):
    grsn = AvGRStreamN(PctStreams,PctGrazing,GrazingAnimal,NumAnimals,AvgAnimalWt,AnimalDailyN)
    if n42 > 0:# based on the code, n42 is always > 0 (may not need to check
        result = (n45 / n42) * n69 * grsn
    else:
        result = 0 #TODO: the code does not have this fall back, would have error if n42 <= 0
    return result


def NFENCING_2(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN,n42,n45,n69):
    if n42 > 0:  # based on the code, n42 is always > 0 (may not need to check
        grsn = AvGRStreamN_2(PctStreams, PctGrazing, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN)
        return (n45 / n42) * n69 * grsn
    else:
        return 0  # TODO: the code does not have this fall back, would have error if n42 <= 0



def NRUNCON(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
            Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate, AWMSNgPct,
            NgAWMSCoeffN,n41f,n85l):
    grlbn = GRLBN(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    nglbn = AvNGLostBarnNSum(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                     Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    result = (n41f / 100) * n85l * (grlbn + nglbn)
    return result


def NRUNCON_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
            Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate, AWMSNgPct,
            NgAWMSCoeffN,n41f,n85l):
    grlbn = GRLBN_2(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                  Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    nglbn = AvNGLostBarnNSum_2(NYrs, NGPctManApp, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                             Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    return (n41f / 100) * n85l * (grlbn + nglbn)




def AvPrecipitation(NYrs, DaysMonth, Prec):
    result = np.zeros((12,))
    precipitation = Precipitation(NYrs, DaysMonth, Prec)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += precipitation[Y][i] / NYrs
    return result


def AvPrecipitation_2(Prec):
    precipitation = Precipitation_2(Prec)
    return np.average(precipitation, axis=0)

NLU = 16
NAnimals = 9
NPConvert = 1


leap_year = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             True, True, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, True, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, True, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, True, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, True, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False]
non_leap_year = [False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, True, True, True, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, True, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, True, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False, True,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                 False, False, False]


def mask_builder(DaysMonth):
    ones = np.ravel(np.ones((12, 31))).astype("int")
    slices = []
    for i, month in enumerate(DaysMonth[0]):
        slices.append(slice(31 * i, 31 * i + month))
    ones[np.r_[tuple(slices)]] = 0
    return ones


def ymd_to_daily(ymd_array, DaysMonth):
    month_maps = map(lambda x: leap_year if x[1] == 29 else non_leap_year, DaysMonth)
    mask = np.ravel(np.array(month_maps))
    x = ma.array(ymd_array, mask=mask)
    return x[~x.mask]


def daily_to_ymd(daily_array, NYrs, DaysMonth):
    result = np.zeros((NYrs * 12 * 31,))
    month_maps = map(lambda x: leap_year if x[1] == 29 else non_leap_year, DaysMonth)
    mask = np.ravel(np.array(month_maps))
    x = ma.array(result, mask=mask)
    x[~x.mask] = daily_array
    return x.reshape((NYrs, 12, 31))


def ymd_to_daily_slow(ymd_array, NYrs, DaysMonth):
    result = []
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result.append(ymd_array[Y][i][j])
    return np.array(result)


# @jit(cache=True, nopython=True)
def get_value_for_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday = variable_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday
                else:
                    yesterday = variable[Y][i][j]


# @jit(cache=True, nopython=True)
def get_value_for_yesterday_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday_yesterday = variable_0
    yesterday = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday_yesterday
                else:
                    yesterday_yesterday = yesterday
                    yesterday = variable[Y][i][j]


# @jit(cache=True, nopython=True)
def get_value_for_yesterday_yesterday_yesterday(variable, variable_0, Y_in, i_in, j_in, NYrs, DaysMonth):
    yesterday_yesterday_yesterday = variable_0
    yesterday_yesterday = 0
    yesterday = 0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if (Y == Y_in and i == i_in and j == j_in):
                    return yesterday_yesterday_yesterday
                else:
                    yesterday_yesterday_yesterday = yesterday_yesterday
                    yesterday_yesterday = yesterday
                    yesterday = variable[Y][i][j]



@memoize
def DailyET(NYrs, DaysMonth, Temp, DayHrs, KV, PcntET, ETFlag):
    result = np.zeros((NYrs, 12, 31))
    # CALCULATE ET FROM SATURATED VAPOR PRESSURE,
    # HAMON (1961) METHOD
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                DailyTemp = Temp[Y][i][j]
                if ETFlag is ETflag.HAMON_METHOD:
                    if DailyTemp > 0:
                        SatVaPressure = (33.8639 * ((0.00738 * DailyTemp +
                                                     0.8072) ** 8 - 0.000019 *
                                                    np.absolute(1.8 * DailyTemp + 48) +
                                                    0.001316))
                        PotenET = (0.021 * DayHrs[i] ** 2 * SatVaPressure / (DailyTemp + 273))
                        ET = KV[i] * PotenET * PcntET[i]
                        result[Y][i][j] = ET
    return result


@memoize
def SatVaPressure(Temp):
    return (33.8639 * ((0.00738 * Temp + 0.8072) ** 8 - 0.000019 * np.absolute(1.8 * Temp + 48) + 0.001316))


@memoize
def PotentET(DayHrs, Temp):
    return np.multiply(0.021 * ((DayHrs ** 2).reshape(12, 1)), SatVaPressure(Temp)) / (Temp + 273)


@memoize
def DailyET_2(Temp, KV, PcntET, DayHrs):
    return np.where(Temp > 0, np.multiply((KV * PcntET).reshape(12, 1), PotentET(DayHrs, Temp)), 0)



def LossFactAdj(NYrs, Prec, DaysMonth):
    result = np.zeros((NYrs, 12))
    precipitation = Precipitation(NYrs, DaysMonth, Prec)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (precipitation[Y][i] / DaysMonth[Y][i]) / 0.3301
    return result

@memoize
def LossFactAdj_2(Prec, DaysMonth):
    return Precipitation_2(Prec) / DaysMonth / 0.3301


def Precipitation(NYrs, DaysMonth, Prec):#TODO: change internal "Precipitation" to "result"
    Precipitation = np.zeros((NYrs,12))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                Precipitation[Y][i] = Precipitation[Y][i] + Prec[Y][i][j]
    return Precipitation

def Precipitation_2(Prec):
    return np.sum(Prec, axis=(2))





@memoize
def PtSrcFlow(NYrs, PointFlow):
    result = np.zeros((NYrs, 12))
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = result[Y][i] + PointFlow[i]
    return result


def PtSrcFlow_2(NYrs, PointFlow):
    return np.repeat(PointFlow[:, None], NYrs, axis=1).T


def AvPtSrcFlow(NYrs, PtSrcFlow):
    result = np.zeros((12,))
    for Y in range(NYrs):
        for i in range(12):
            result[i] += PtSrcFlow[Y][i] / NYrs
    return result


def AvPtSrcFlow_2(PointFlow):
    return PointFlow






def AnimalN(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate):
    result = np.zeros((NYrs, 12))
    ng_lost_man_n = NGLostManN(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate,
                               Prec, DaysMonth,
                               NGPctSoilIncRate)
    gr_lost_man_n = GRLostManN(NYrs, GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRAppNRate,
                               Prec, DaysMonth, GRPctSoilIncRate)
    ng_lost_barn_n = NGLostBarnN(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                                 Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    gr_lost_barn_n = GRLostBarnN(NYrs, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                                 GRBarnNRate, Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN)
    gr_loss_n = GRLossN(NYrs, PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                        GrazingNRate, Prec,
                        DaysMonth)
    gr_stream_n = GRStreamN(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (ng_lost_man_n[Y][i]
                            + gr_lost_man_n[Y][i]
                            + ng_lost_barn_n[Y][i]
                            + gr_lost_barn_n[Y][i]
                            + gr_loss_n[Y][i]
                            + gr_stream_n[i])
    return result

@memoize
def AnimalN_2(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
              NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
              RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate):
    ng_lost_man_n = NGLostManN_2(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate,
                                 Prec, DaysMonth, NGPctSoilIncRate)
    gr_lost_man_n = GRLostManN_2(NYrs, GRPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRAppNRate,
                                 Prec, DaysMonth, GRPctSoilIncRate)
    ng_lost_barn_n = NGLostBarnN_2(NYrs, NGPctManApp, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                   NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN)
    gr_lost_barn_n = GRLostBarnN_2(NYrs, Prec, DaysMonth, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                   GRPctManApp, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, RunContPct,
                                   RunConCoeffN)
    gr_loss_n = GRLossN_2(NYrs, PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                          GrazingNRate, Prec,
                          DaysMonth)
    gr_stream_n = np.reshape(
        np.repeat(GRStreamN_2(PctStreams, PctGrazing, GrazingAnimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN),
                  repeats=NYrs, axis=0), (NYrs, 12))
    return ng_lost_man_n + gr_lost_man_n + ng_lost_barn_n + gr_lost_barn_n + gr_loss_n + gr_stream_n


def AvAnimalN(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams,GrazingNRate):
    result = np.zeros((12,))
    animal_n = AnimalN(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams,GrazingNRate)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += animal_n[Y][i] / NYrs
    return result


def AvAnimalN_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams,GrazingNRate):
    return np.sum(AnimalN_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate))/NYrs



def AvAnimalNSum(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
                 NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
                 RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate):
    av_animal_n = AvAnimalN(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec,
                            DaysMonth,
                            NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct,
                            NgAWMSCoeffN,
                            RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams,
                            GrazingNRate)
    result = sum(av_animal_n)
    return result


def AvAnimalNSum_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec, DaysMonth,
                 NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN,
                 RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate):
    return np.sum(AvAnimalN_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, Prec,
                            DaysMonth, NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate,
                            AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct,
                            GrAWMSCoeffN, PctStreams, GrazingNRate))



def AvAnimalNSum_1(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
                   GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
                   Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp,
                   AWMSNgPct, NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    n7b = N7b(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
              GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate, Prec, DaysMonth, AWMSGrPct,
              GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct, NGBarnNRate, NgAWMSCoeffN,
              n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64)
    result = n7b
    return result

@memoize
def AvAnimalNSum_1_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
                   GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
                   Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp,
                   AWMSNgPct, NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    return N7b_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
        GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate, Prec, DaysMonth, AWMSGrPct,
        GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct, NGBarnNRate, NgAWMSCoeffN,
        n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64)



def N7b(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
        GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
        Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct,
        NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    av_animal_n_sum = AvAnimalNSum(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                   NGAppNRate,
                                   Prec, DaysMonth,
                                   NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct,
                                   NgAWMSCoeffN,
                                   RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN,
                                   PctStreams, GrazingNRate)
    nawmsl = NAWMSL(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                    Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h)
    nawmsp = NAWMSP(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                    Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j)
    nruncon = NRUNCON(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                      GRBarnNRate,
                      Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate,
                      AWMSNgPct, NgAWMSCoeffN, n41f, n85l)
    nfencing = NFENCING(PctStreams, PctGrazing, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, n42, n45, n69)
    nagbuffer = NAGBUFFER(n42, n43, n64, NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                          NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, GRPctManApp,
                          PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate,
                          GRAppNRate, GRPctSoilIncRate, GrazingNRate)
    result = av_animal_n_sum - (nawmsl + nawmsp + nruncon + nfencing + nagbuffer)
    return result


def N7b_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
          GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
          Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct,
          NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    av_animal_n_sum = AvAnimalNSum_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                     NGAppNRate, Prec, DaysMonth, NGPctSoilIncRate, GRPctManApp, GRAppNRate,
                                     GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN,
                                     PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate)
    nawmsl = NAWMSL_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                    Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h)
    nawmsp = NAWMSP_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                    Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j)
    nruncon = NRUNCON_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                      GRBarnNRate,
                      Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate,
                      AWMSNgPct, NgAWMSCoeffN, n41f, n85l)
    nfencing = NFENCING_2(PctStreams, PctGrazing, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, n42, n45, n69)
    nagbuffer = NAGBUFFER_2(n42, n43, n64, NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                          NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, GRPctManApp,
                          PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate,
                          GRAppNRate, GRPctSoilIncRate, GrazingNRate)
    result = av_animal_n_sum - (nawmsl + nawmsp + nruncon + nfencing + nagbuffer)
    return result



def N7b_1(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
          GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate, Prec, DaysMonth, AWMSGrPct,
          GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct, NGBarnNRate, NgAWMSCoeffN, n41d,
          n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64, NPConvert):
    n7b = N7b(NYrs, GrazingAnimal, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
              GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate, Prec, DaysMonth, AWMSGrPct,
              GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct, NGBarnNRate, NgAWMSCoeffN,
              n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64)
    result = n7b * NPConvert
    return result


def N7b_1_2():
    pass


