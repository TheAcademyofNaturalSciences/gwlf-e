import numpy as np
from Timer import time_function
import Grow_Factor

def PondPhosLoad(NYrs, DaysMonth, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow):
    result = np.zeros((NYrs,12,31))
    grow_factor = Grow_Factor.Grow_Factor(NYrs, DaysMonth, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = (NumPondSys[i] * (PhosSepticLoad - PhosPlantUptake * grow_factor[i]))
    return result


def PondPhosLoad_2():
    pass
