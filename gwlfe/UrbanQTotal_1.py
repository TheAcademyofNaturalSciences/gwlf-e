import numpy as np
from Timer import time_function
from Water import Water
from QrunI import QrunI
from QrunP import QrunP
from NLU import  NLU

def UrbanQTotal_1(NYrs, DaysMonth,Temp, Prec,InitialSnow, NRur, NUrb, cni,UrbAreaTotal, AntMoist,Grow, cnp,Imper, ISRR, ISRA, Area):
    result = np.zeros((NYrs,12,31))
    water = Water(NYrs, DaysMonth, Temp, Prec,InitialSnow)
    qrun_i = QrunI(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cni, Grow)
    qrun_p = QrunP(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cnp, Grow)
    nlu = NLU(NRur, NUrb)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0:
                    pass
                else:
                    if water[Y][i][j] > 0.01:
                        result[Y][i][j] = 0
                        for l in range(NRur, nlu):
                            lu = l - NRur
                            if UrbAreaTotal > 0:
                                result[Y][i][j] += ((qrun_i[Y][i][j][l] * (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))
                                                   + qrun_p[Y][i][j][l] * (1 - (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))))
                                                  * Area[l] / UrbAreaTotal)
    return result

def UrbanQTotal_1_2():
    pass
