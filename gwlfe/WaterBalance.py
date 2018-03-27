import numpy as np
from Timer import time_function


def WaterBalance(NYrs,DaysMonth,QTotal,DailyWater,RecessionCoef,SeepCoef,ET_Part1,MaxWaterCap,DayRunoff,TotAreaMeters):
    SatStor = 0
    result = np.zeros((NYrs,12,31,7))
    Perc = np.zeros((NYrs,12,31))
    PercCm = np.zeros((NYrs,12,31))
    DailyFlow = np.zeros((NYrs,12,31))
    DailyFlowGPM = np.zeros((NYrs,12,31))
    DailyGrFlow = np.zeros((NYrs,12,31))
    UnsatStor = np.zeros((NYrs,12,31))
    Infiltration = np.zeros((NYrs,12,31))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                # ***** WATERSHED WATER BALANCE *****
                Water = DailyWater[Y][i][j]
                if QTotal[Y][i][j] <= Water:
                    Infiltration[Y][i][j] = Water - QTotal[Y][i][j]
                GrFlow = RecessionCoef * SatStor
                DeepSeep = SeepCoef * SatStor

                # CALCULATE EVAPOTRANSPIRATION, Percolation, AND THE
                # NEXT DAY'S UNSATURATED STORAGE AS LIMITED BY THE UNSATURATED
                # ZONE MAXIMUM WATER CAPACITY

                UnsatStor[Y][i][j] = UnsatStor[Y][i][j] + Infiltration[Y][i][j]

                # Calculate water balance for non-Pesticide componenets
                if ET_Part1[Y][i][j] >= UnsatStor[Y][i][j]:
                    # z.ET = z.UnsatStor
                    UnsatStor[Y][i][j] = 0
                else:
                    UnsatStor[Y][i][j] = UnsatStor[Y][i][j] - ET_Part1[Y][i][j]

                # Obtain the Percolation, adjust precip and UnsatStor values
                if UnsatStor[Y][i][j] > MaxWaterCap:
                    Percolation = UnsatStor[Y][i][j] - MaxWaterCap
                    Perc[Y][i][j] = UnsatStor[Y][i][j] - MaxWaterCap
                    UnsatStor[Y][i][j] = UnsatStor[Y][i][j] - Percolation
                else:
                    Percolation = 0
                    Perc[Y][i][j] = 0
                PercCm[Y][i][j] = Percolation / 100
                # print (z.SatStor)
                # CALCULATE STORAGE IN SATURATED ZONES AND GROUNDWATER
                # DISCHARGE
                SatStor = SatStor + Percolation - GrFlow - DeepSeep
                if SatStor < 0:
                    SatStor = 0

                Flow = QTotal[Y][i][j] + GrFlow
                DailyFlow[Y][i][j] = DayRunoff[Y][i][j] + GrFlow

                DailyFlowGPM[Y][i][j] = Flow * 0.00183528 * TotAreaMeters
                DailyGrFlow[Y][i][j] = GrFlow  # (for daily load calculations)
    result[:,:,:,0] = Perc
    result[:,:,:,1] = PercCm
    result[:,:,:,2] = DailyFlow
    result[:,:,:,3] = DailyFlowGPM
    result[:,:,:,4] = DailyGrFlow
    result[:,:,:,5] = UnsatStor
    result[:,:,:,6] = Infiltration
    return result


def WaterBalance_2():
    pass

def MonthFlow(NYrs,DaysMonth,DailyFlow):
    # MONTHLY FLOW
    result = np.zeros((NYrs,12))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + DailyFlow[Y][i][j]
    return result

def MonthFlow_2():
    pass

def StreamFlow(NYrs,DaysMonth,DailyFlow):
    result = np.zeros((NYrs, 12))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + DailyFlow[Y][i][j]
    return result

def StreamFlow_2():
    pass

def GroundWatLE(NYrs,DaysMonth,DailyGrFlow):
    result = np.zeros((NYrs, 12))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] +DailyGrFlow[Y][i][j]
    return result

def GroundWatLE_2():
    pass