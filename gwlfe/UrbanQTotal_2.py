import numpy as np
from Timer import time_function
from UrbanQTotal_1 import UrbanQTotal_1

def UrbanQTotal_2(NYrs,DaysMonth,DailyTemp,Water,UrbAreaTotal,NRur, NLU,QrunI, Imper, ISRR, ISRA, QrunP, Area, AreaTotal):
    result = np.zeros((NYrs,12,31))
    urban_q_total_1 = UrbanQTotal_1(NYrs, DaysMonth,Temp, Prec,InitialSnow, NRur, NUrb, cni,UrbAreaTotal, AntMoist,Grow, cnp,Imper, ISRR, ISRA, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if DailyTemp <= 0:
                    pass
                else:
                    if Water[Y][i][j] > 0.01:
                        if UrbAreaTotal > 0:
                            result = urban_q_total_1*UrbAreaTotal / AreaTotal
                        else:
                            result = 0
    return result


def UrbanQTotal_2_2():
    pass
