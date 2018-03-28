import numpy as np
from Timer import time_function
import Water
import Retention
import Qrun


def RuralQTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow, RurAreaTotal, Area, AreaTotal):
    result = np.zeros((NYrs, 12, 31))
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    retention = Retention.Retention(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    qrun = Qrun.Qrun(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if CN[l] > 0:
                        if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                            result[Y][i][j] += qrun[Y][i][j][l] * Area[l] / RurAreaTotal
                if RurAreaTotal > 0:
                    result[Y][i][j] *= RurAreaTotal / AreaTotal
                else:
                    result[Y][i][j] = 0
    return result

def RuralQTotal_2():
    pass
