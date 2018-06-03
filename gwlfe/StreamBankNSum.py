import numpy as np
from Timer import time_function
from Memoization import memoize
from StreamBankN_1 import StreamBankN_1
from StreamBankN_1 import StreamBankN_1_2
from NSTAB import NSTAB
from NFEN import NFEN
from NURBBANK import NURBBANK


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
