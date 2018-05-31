import numpy as np
from Timer import time_function
from Memoization import memoize
from StreamBankEros_1 import StreamBankEros_1
from StreamBankEros_1 import StreamBankEros_1_2


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