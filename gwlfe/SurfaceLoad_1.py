import numpy as np
from Timer import time_function
from Memoization import memoize
from Water import Water
from Water import Water_2
from NLU_function import NLU_function
from AdjUrbanQTotal_1 import AdjUrbanQTotal_1
from AdjUrbanQTotal_1 import AdjUrbanQTotal_1_2
from SurfaceLoad import SurfaceLoad
from SurfaceLoad import SurfaceLoad_2
from RetentionEff import RetentionEff
from RetentionEff import RetentionEff_2
from FilterEff import FilterEff
from FilterEff import FilterEff_2


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
