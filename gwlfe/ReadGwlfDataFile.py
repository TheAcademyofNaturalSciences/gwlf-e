# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

"""
Initialize variables and perfom some preliminary calculations.

Imported from ReadAllDataFiles.bas
"""

import logging
from FlowDays import FlowDays
from .enums import SweepType, YesOrNo
from PrelimQualCalculations import ReDimRunQualVars

log = logging.getLogger(__name__)

from AFOS.GrazingAnimals.Loads.GrazingN import GrazingN_2
from AFOS.GrazingAnimals.Losses.GRStreamN import GRStreamN_2
from AFOS.GrazingAnimals.Loads.GRAccManAppN import GRAccManAppN_2
from AFOS.nonGrazingAnimals.Loads.NGAppManN import NGAppManN_2
from AFOS.nonGrazingAnimals.Losses.NGLostBarnN import NGLostBarnN_2
from AFOS.GrazingAnimals.Losses.GRLostBarnN import GRLostBarnN_2
from AFOS.GrazingAnimals.Losses.GRLostManN import GRLostManN_2
from AFOS.nonGrazingAnimals.Losses.NGLostManN import NGLostManN_2
from AFOS.GrazingAnimals.Losses.GRLossN import GRLossN_2
from GrazingAnimal import GrazingAnimal


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
