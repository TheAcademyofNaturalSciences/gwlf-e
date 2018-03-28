#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

"""
Runs the GWLF-E MapShed model.

Imported from GWLF-E.frm
"""

import logging

import numpy as np

from .enums import ETflag, GrowFlag
from . import ReadGwlfDataFile
from . import PrelimCalculations
from . import CalcCnErosRunoffSed
from . import AFOS
from . import CalcLoads
from . import StreamBank
from . import AnnualMeans
from . import WriteOutputFiles
import Precipitation
import ET
import PtSrcFlow
import InitSnow
import Grow_Factor
import PondPhosLoad
import FrozenPondPhos
import PhosPondOverflow
import MonthPondPhos
import MonthShortPhos
import MonthDischargePhos
import DisSeptPhos
import SepticPhos
import AvSeptPhos
import Water
import Rain
import AMC5
#import NLU
import NewCN
import CNum
import Retention
import CNI
import CNP
import CNumPerv
import Qrun
import AgAreaTotal
import AgQTotal
import RuralQTotal
import CNumImperv
import CNumPervReten
import CNumImpervReten
import AgRunoff
import TileDrainRO
import QrunP
import QrunI
log = logging.getLogger(__name__)


def run(z):
    log.debug('Running model...')

    # Raise exception instead of printing a warning for floating point
    # overflow, underflow, and division by 0 errors.
    np.seterr(all='raise')

    ReadGwlfDataFile.ReadAllData(z)

    # CALCLULATE PRELIMINARY INITIALIZATIONS AND VALUES FOR
    # WATER BALANCE AND NUTRIENTS
    PrelimCalculations.InitialCalculations(z)

    # MODEL CALCULATIONS FOR EACH YEAR OF ANALYSIS - WATER BALANCE,
    # NUTRIENTS AND SEDIMENT LOADS

    z.Precipitation = Precipitation.Precipitation(z.NYrs, z.DaysMonth, z.Prec)
    # z.Precipitation = Precipitation.Precipitation_2(z.Prec)
    # if (z.Precipitation.any() == z.Precipitation_vect.any()):
    # print ('True')

    # DailyET_Part1 = ET.DailyET(z.NYrs,z.DaysMonth,z.Temp,z.DayHrs,z.KV,z.PcntET,z.ETFlag)
    DailyET_Part1 = ET.DailyET_2(z.Temp, z.KV, z.PcntET, z.DayHrs)
    # if (DailyET_Part1_vect.any() == DailyET_Part1.any()):
    # print ('True')

    # z.PtSrcFlow = PtSrcFlow.PtSrcFlow(z.NYrs,z.PointFlow)
    z.PtSrcFlow = PtSrcFlow.PtSrcFlow_2(z.NYrs,z.PointFlow)

    z.Grow_Factor = Grow_Factor.Grow_Factor(z.NYrs, z.DaysMonth, z.Grow)

    #z.InitialSnow = z.InitSnow
    z.InitSnow,z.MeltPest = InitSnow.InitSnow(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow)

    z.PondPhosLoad = PondPhosLoad.PondPhosLoad(z.NYrs, z.DaysMonth, z.NumPondSys, z.PhosSepticLoad, z.PhosPlantUptake
                                               , z.Grow)

    z.FrozenPondPhos = FrozenPondPhos.FrozenPondPhos(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.NumPondSys
                                                , z.PhosSepticLoad, z.PhosPlantUptake, z.Grow)

    z.PhosPondOverflow = PhosPondOverflow.PhosPondOverflow(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow
                                                , z.NumPondSys, z.PhosSepticLoad, z.PhosPlantUptake, z.Grow)

    z.MonthPondPhos = MonthPondPhos.MonthPondPhos(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.NumPondSys
                                                , z.PhosSepticLoad, z.PhosPlantUptake, z.Grow)

    z.MonthShortPhos = MonthShortPhos.MonthShortPhos(z.NYrs, z.DaysMonth, z.PhosSepticLoad, z.PhosPlantUptake, z.Grow)

    z.MonthDischargePhos = MonthDischargePhos.MonthDischargePhos(z.NYrs, z.DaysMonth, z.PhosSepticLoad)

    z.DisSeptPhos = DisSeptPhos.DisSeptPhos(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.NumPondSys
                                                , z.NumShortSys, z.NumDischargeSys, z.PhosSepticLoad, z.PhosPlantUptake
                                                , z.Grow)

    z.SepticPhos = SepticPhos.SepticPhos(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.NumPondSys
                                                , z.NumShortSys, z.NumDischargeSys, z.PhosSepticLoad, z.PhosPlantUptake
                                                , z.Grow)

    z.AvSeptPhos = AvSeptPhos.AvSeptPhos(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.NumPondSys
                                                , z.NumShortSys, z.NumDischargeSys, z.PhosSepticLoad
                                                , z.PhosPlantUptake, z.Grow)

    z.Water = Water.Water(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow)

    z.Rain = Rain.Rain(z.NYrs, z.DaysMonth, z.Temp, z.Prec)

    z.AMC5= AMC5.AMC5(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist)

    #z.NLU = NLU.NLU(z.NRur, z.NUrb)

    z.NewCN = NewCN.NewCN(z.CN, z.NRur, z.NLU)

    z.CNum = CNum.CNum(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU, z.Grow)

    z.Retention = Retention.Retention(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU, z.Grow)

    z.CNI = CNI.CNI(z.NRur, z.NLU, z.CNI)

    z.CNP = CNP.CNP(z.NRur, z.NLU, z.CNP)

    z.CNumPerv = CNumPerv.CNumPerv(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CNP, z.NRur, z.NLU, z.Grow)

    z.Qrun = Qrun.Qrun(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU, z.Grow)

    z.AgAreaTotal = AgAreaTotal.AgAreaTotal(z.NRur, z.Landuse, z.Area)

    z.AgQTotal = AgQTotal.AgQTotal(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU,
                                   z.Grow, z.Landuse, z.Area)

    z.RuralQTotal = RuralQTotal.RuralQTotal(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU, z.Grow, z.RurAreaTotal, z.Area, z.AreaTotal)

    z.CNumImperv = CNumImperv.CNumImperv(z.NYrs, z.DaysMonth, z.NRur, z.NLU, z.CNI, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.Grow)

    z.CNumPervReten = CNumPervReten.CNumPervReten(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.NRur, z.NLU, z.CNP, z.Grow)

    z.CNumImpervReten = CNumImpervReten.CNumImpervReten(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.NRur, z.NLU, z.CNI, z.Grow)

    z.AgRunoff = AgRunoff.AgRunoff(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur, z.NLU,
                                   z.Grow, z.Landuse, z.Area)

    z.TileDrainRO = TileDrainRO.TileDrainRO(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.CN, z.NRur,
                                           z.NLU, z.Grow, z.Landuse, z.Area, z.TileDrainDensity)

    z.QrunP = QrunP.QrunP(z.NYrs, z.DaysMonth ,z. Temp, z.Prec, z.InitialSnow, z.AntMoist, z.NRur, z.NLU, z.CNP, z.Grow)

    z.QrunI = QrunI.QrunI(z.NYrs, z.DaysMonth, z.Temp, z.Prec, z.InitialSnow, z.AntMoist, z.NRur, z.NLU, z.CNI, z.Grow)

    for Y in range(z.NYrs):
        # Initialize monthly septic system variables
        z.MonthPondNitr = np.zeros(12)
        #z.MonthPondPhos = np.zeros(12)
        z.MonthNormNitr = np.zeros(12)
        z.MonthShortNitr = np.zeros(12)
        #z.MonthShortPhos = np.zeros(12)
        z.MonthDischargeNitr = np.zeros(12)
        #z.MonthDischargePhos = np.zeros(12)

        # FOR EACH MONTH...
        for i in range(12):
            # LOOP THROUGH NUMBER OF LANDUSES IN THE BASIN TO GET QRUNOFF
            for l in range(z.NLU):
                z.QRunoff[l, i] = 0
                z.AgQRunoff[l, i] = 0
                z.ErosWashoff[l, i] = 0
                z.RurQRunoff[l, i] = 0
                z.UrbQRunoff[l, i] = 0
                z.LuErosion[Y, l] = 0

            # DAILY CALCULATIONS
            for j in range(z.DaysMonth[Y][i]):
                # DAILYWEATHERANALY TEMP[Y][I][J], PREC[Y][I][J]
                # ***** BEGIN WEATHER DATA ANALYSIS *****
                z.DailyTemp = z.Temp[Y][i][j]
                z.DailyPrec = z.Prec[Y][i][j]
                #z.Melt = 0
                #z.Rain = 0
                #z.Water = 0
                z.Erosiv = 0
                z.ET = 0
                z.QTotal = 0
                # z.AgQTotal = 0
                # z.RuralQTotal = 0
                z.UrbanQTotal = 0

                # Question: Are these values supposed to accumulate for each
                # day, each month, and each year? Or should these be
                # re-initialized to a default value at some point?
                for l in range(z.NLU):
                    z.ImpervAccum[l] = (z.ImpervAccum[l] * np.exp(-0.12) +
                                        (1 / 0.12) * (1 - np.exp(-0.12)))
                    z.PervAccum[l] = (z.PervAccum[l] * np.exp(-0.12) +
                                      (1 / 0.12) * (1 - np.exp(-0.12)))

                # TODO: If Water is <= 0.01, then CalcCNErosRunoffSed
                # never executes, and CNum will remain undefined.
                # What should the default value for CNum be in this case?
                #z.CNum = 0

                # RAIN , SNOWMELT, EVAPOTRANSPIRATION (ET)
                if z.DailyTemp <= 0:
                    #z.InitSnow = z.InitSnow + z.DailyPrec
                    pass
                else:
                    # z.Rain = z.DailyPrec
                    # if z.InitSnow > 0.001:
                    #     # A DEGREE-DAY INITSNOW MELT, BUT NO MORE THAN EXISTED
                    #     # INITSNOW
                    #     z.Melt = 0.45 * z.DailyTemp
                    #     z.MeltPest[Y][i][j] = z.Melt
                    #     if z.Melt > z.InitSnow[Y][i][j]:
                    #         #z.Melt = z.InitSnow[Y][i][j]
                    #         #z.MeltPest[Y][i][j] = z.InitSnow
                    #         pass
                    #     #z.InitSnow = z.InitSnow - z.Melt
                    #     pass
                    # else:
                    #     z.MeltPest[Y][i][j] = 0

                    # AVAILABLE WATER CALCULATION
                    # z.Water = z.Rain[Y][i][j] + z.MeltPest[Y][i][j]
                    z.DailyWater[Y][i][j] = z.Water[Y][i][j]

                    # Compute erosivity when erosion occurs, i.e., with rain and no InitSnow left
                    if z.Rain[Y][i][j] > 0 and z.InitSnow[Y][i][j] < 0.001:
                        z.Erosiv = 6.46 * z.Acoef[i] * z.Rain[Y][i][j] ** 1.81

                    # IF WATER AVAILABLE, THEN CALL SUB TO COMPUTE CN, RUNOFF,
                    # EROSION AND SEDIMENT
                    if z.Water[Y][i][j] > 0.01:
                        CalcCnErosRunoffSed.CalcCN(z, i, Y, j)

                # DAILY CN
                #z.DailyCN[Y][i][j] = z.CNum[Y][i][j] #Do we need to keep DailyCN?

                # UPDATE ANTECEDENT RAIN+MELT CONDITION
                # Subtract AMC5 by the sum of AntMoist (day 5) and Water
                #z.AMC5 = z.AMC5 - z.AntMoist[4] + z.Water[Y][i][j]
                z.DailyAMC5[Y][i][j] = z.AMC5[Y][i][j]

                # Shift AntMoist values to the right.
                # z.AntMoist[4] = z.AntMoist[3]
                # z.AntMoist[3] = z.AntMoist[2]
                # z.AntMoist[2] = z.AntMoist[1]
                # z.AntMoist[1] = z.AntMoist[0]
                # z.AntMoist[0] = z.Water[Y][i][j]

                # CALCULATE ET FROM SATURATED VAPOR PRESSURE,
                # HAMON (1961) METHOD
                # if z.ETFlag is ETflag.HAMON_METHOD:
                #     if z.DailyTemp > 0:
                #         z.SatVaPressure = (33.8639 * ((0.00738 * z.DailyTemp +
                #                            0.8072) ** 8 - 0.000019 *
                #                            np.absolute(1.8 * z.DailyTemp + 48) +
                #                            0.001316))
                #         z.PotenET = (0.021 * z.DayHrs[i] ** 2 * z.SatVaPressure
                #                      / (z.DailyTemp + 273))
                #         z.ET = z.KV[i] * z.PotenET * z.PcntET[i]

                # Daily ET calculation
                # z.DailyET[Y][i][j] = z.ET
                # if (z.DailyET.any() == DailyET_Part1.any()):
                # print ('True')
                z.ET = DailyET_Part1[Y][i][j]
                z.DailyET[Y][i][j] = z.ET

                # ***** END WEATHER DATA ANALYSIS *****

                # ***** WATERSHED WATER BALANCE *****

                if z.QTotal <= z.Water[Y][i][j]:
                    z.Infiltration = z.Water[Y][i][j] - z.QTotal
                z.GrFlow = z.RecessionCoef * z.SatStor
                z.DeepSeep = z.SeepCoef * z.SatStor

                # CALCULATE EVAPOTRANSPIRATION, Percolation, AND THE
                # NEXT DAY'S UNSATURATED STORAGE AS LIMITED BY THE UNSATURATED
                # ZONE MAXIMUM WATER CAPACITY

                z.UnsatStor = z.UnsatStor + z.Infiltration

                # Calculate water balance for non-Pesticide componenets
                if z.ET >= z.UnsatStor:
                    z.ET = z.UnsatStor
                    z.UnsatStor = 0
                else:
                    z.UnsatStor = z.UnsatStor - z.ET

                # Obtain the Percolation, adjust precip and UnsatStor values
                if z.UnsatStor > z.MaxWaterCap:
                    z.Percolation = z.UnsatStor - z.MaxWaterCap
                    z.Perc[Y][i][j] = z.UnsatStor - z.MaxWaterCap
                    z.UnsatStor = z.UnsatStor - z.Percolation
                else:
                    z.Percolation = 0
                    z.Perc[Y][i][j] = 0
                z.PercCm[Y][i][j] = z.Percolation / 100

                # CALCULATE STORAGE IN SATURATED ZONES AND GROUNDWATER
                # DISCHARGE
                z.SatStor = z.SatStor + z.Percolation - z.GrFlow - z.DeepSeep
                if z.SatStor < 0:
                    z.SatStor = 0
                z.Flow = z.QTotal + z.GrFlow
                z.DailyFlow[Y][i][j] = z.DayRunoff[Y][i][j] + z.GrFlow

                z.DailyFlowGPM[Y][i][j] = z.Flow * 0.00183528 * z.TotAreaMeters
                z.DailyGrFlow[Y][i][j] = z.GrFlow  # (for daily load calculations)

                # MONTHLY FLOW
                z.MonthFlow[Y][i] = z.MonthFlow[Y][i] + z.DailyFlow[Y][i][j]

                # CALCULATE TOTALS
                # z.Precipitation[Y][i] = z.Precipitation[Y][i] + z.Prec[Y][i][j]
                z.Evapotrans[Y][i] = z.Evapotrans[Y][i] + z.ET

                z.StreamFlow[Y][i] = z.StreamFlow[Y][i] + z.Flow
                z.GroundWatLE[Y][i] = z.GroundWatLE[Y][i] + z.GrFlow

                #grow_factor = GrowFlag.intval(z.Grow[i])

                # CALCULATE DAILY NUTRIENT LOAD FROM PONDING SYSTEMS
                z.PondNitrLoad = (z.NumPondSys[i] *
                                  (z.NitrSepticLoad - z.NitrPlantUptake * z.Grow_Factor[i]))
                #z.PondPhosLoad = (z.NumPondSys[i] *
                                 #(z.PhosSepticLoad - z.PhosPlantUptake * z.Grow_Factor[i]))

                # UPDATE MASS BALANCE ON PONDED EFFLUENT
                if z.Temp[Y][i][j] <= 0 or z.InitSnow[Y][i][j] > 0:

                    # ALL INPUTS GO TO FROZEN STORAGE
                    z.FrozenPondNitr = z.FrozenPondNitr + z.PondNitrLoad
                    #z.FrozenPondPhos = z.FrozenPondPhos + z.PondPhosLoad[Y][i][j]

                    # NO NUTIENT OVERFLOW
                    z.NitrPondOverflow = 0
                    #z.PhosPondOverflow = 0
                else:
                    z.NitrPondOverflow = z.FrozenPondNitr + z.PondNitrLoad
                    #z.PhosPondOverflow = z.FrozenPondPhos[Y][i][j] + z.PondPhosLoad[Y][i][j]
                    z.FrozenPondNitr = 0
                    #z.FrozenPondPhos = 0

                # Obtain the monthly Pond nutrients
                z.MonthPondNitr[i] = z.MonthPondNitr[i] + z.NitrPondOverflow
                #z.MonthPondPhos[i] = z.MonthPondPhos[i] + z.PhosPondOverflow[Y][i][j]

                #grow_factor = GrowFlag.intval(z.Grow[i])

                # Obtain the monthly Normal Nitrogen
                z.MonthNormNitr[i] = (z.MonthNormNitr[i] + z.NitrSepticLoad -
                                      z.NitrPlantUptake * z.Grow_Factor[i])

                # 0.56 IS ATTENUATION FACTOR FOR SOIL LOSS
                # 0.66 IS ATTENUATION FACTOR FOR SUBSURFACE FLOW LOSS
                z.MonthShortNitr[i] = (z.MonthShortNitr[i] + z.NitrSepticLoad -
                                       z.NitrPlantUptake * z.Grow_Factor[i])
                #z.MonthShortPhos[i] = (z.MonthShortPhos[i] + z.PhosSepticLoad -
                                       #z.PhosPlantUptake * z.Grow_Factor[i])
                z.MonthDischargeNitr[i] = z.MonthDischargeNitr[i] + z.NitrSepticLoad
                #z.MonthDischargePhos[i] = z.MonthDischargePhos[i] + z.PhosSepticLoad

            # CALCULATE WITHDRAWAL AND POINT SOURCE FLOW VALUES
            z.Withdrawal[Y][i] = (z.Withdrawal[Y][i] + z.StreamWithdrawal[i] +
                                  z.GroundWithdrawal[i])
            # z.PtSrcFlow[Y][i] = z.PtSrcFlow[Y][i] + z.PointFlow[i]

            # CALCULATE THE SURFACE RUNOFF PORTION OF TILE DRAINAGE
            # z.TileDrainRO[Y][i] = (z.TileDrainRO[Y][i] + [z.AgRunoff[Y][i] *
            #                                               z.TileDrainDensity])

            # CALCULATE SUBSURFACE PORTION OF TILE DRAINAGE
            if z.AreaTotal > 0:
                z.GwAgLE[Y][i] = (z.GwAgLE[Y][i] + (z.GroundWatLE[Y][i] *
                                                    (z.AgAreaTotal / z.AreaTotal)))
            z.TileDrainGW[Y][i] = (z.TileDrainGW[Y][i] + [z.GwAgLE[Y][i] *
                                                          z.TileDrainDensity])

            # ADD THE TWO COMPONENTS OF TILE DRAINAGE FLOW
            z.TileDrain[Y][i] = (z.TileDrain[Y][i] + z.TileDrainRO[Y][i] +
                                 z.TileDrainGW[Y][i])

            # ADJUST THE GROUNDWATER FLOW
            z.GroundWatLE[Y][i] = z.GroundWatLE[Y][i] - z.TileDrainGW[Y][i]
            if z.GroundWatLE[Y][i] < 0:
                z.GroundWatLE[Y][i] = 0

            # ADJUST THE SURFACE RUNOFF
            z.Runoff[Y][i] = z.Runoff[Y][i] - z.TileDrainRO[Y][i]

            if z.Runoff[Y][i] < 0:
                z.Runoff[Y][i] = 0

        # CALCULATE ANIMAL FEEDING OPERATIONS OUTPUT
        AFOS.AnimalOperations(z, Y)

        # CALCULATE NUTRIENT AND SEDIMENT LOADS
        CalcLoads.CalculateLoads(z, Y)

        # CALCULATE STREAM BANK EROSION
        StreamBank.CalculateStreamBankEros(z, Y)

        # CALCULATE FINAL ANNUAL MEAN LOADS
        AnnualMeans.CalculateAnnualMeanLoads(z, Y)

    # CALCULATE FINAL MONTHLY AND ANNUAL WATER BALANCE FOR
    # AVERAGE STREAM FLOW

    for i in range(12):
        z.AvStreamFlow[i] = (z.AvRunoff[i] + z.AvGroundWater[i] +
                             z.AvPtSrcFlow[i] + z.AvTileDrain[i] -
                             z.AvWithdrawal[i])

        z.AvCMStream[i] = (z.AvStreamFlow[i] / 100) * z.TotAreaMeters
        if z.AvCMStream[i] > 0:
            z.AvOrgConc[i] = (z.AvTotalOrgs[i] / (z.AvCMStream[i] * 1000)) / 10
        else:
            z.AvOrgConc[i] = 0
    z.AvOrgConc[0] = 0

    z.AvStreamFlowSum = (z.AvRunoffSum + z.AvGroundWaterSum +
                         z.AvPtSrcFlowSum + z.AvTileDrainSum -
                         z.AvWithdrawalSum)

    log.debug("Model run complete for " + str(z.NYrs) + " years of data.")

    output = WriteOutputFiles.WriteOutput(z)
    # WriteOutputFiles.WriteOutputSumFiles()

    return output
