import numpy as np
from Timer import time_function
import QrunI
import QrunP

def UrbanQTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, cni, cnp, Grow, Imper, ISRA, ISRR, Area, UrbAreaTotal, AreaTotal):
    result_1 = np.zeros((NYrs,12,31))
    result_2 = np.zeros((NYrs,12,31))
    qruni = QrunI.QrunI(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, cni, Grow)
    qrunp = QrunP.QrunP(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, cnp, Grow)

    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result_1[Y][i][j] = 0
                result_2[Y][i][j] = 0
                for l in range(NRur, NLU):
                    lu = l - NRur
                    if UrbAreaTotal > 0:
                        result_1[Y][i][j] += ((qruni[Y][i][j][l] * (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))
                                           + qrunp[Y][i][j][l] * (
                                                       1 - (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))))
                                          * Area[l] / UrbAreaTotal)
                        result_2[Y][i][j] += ((qruni[Y][i][j][l] * (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))
                                           + qrunp[Y][i][j][l] * (
                                                       1 - (Imper[l] * (1 - ISRR[lu]) * (1 - ISRA[lu]))))
                                          * Area[l] / UrbAreaTotal)

                if UrbAreaTotal > 0:
                    result_2[Y][i][j] *= UrbAreaTotal / AreaTotal
                else:
                    result_2[Y][i][j] = 0
    return result_1, result_2


def UrbanQTotal_2():
    pass
