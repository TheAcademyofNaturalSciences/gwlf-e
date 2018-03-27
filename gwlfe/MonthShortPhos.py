import numpy as np
from Timer import time_function
import Grow_Factor

def MonthShortPhos(NYrs, DaysMonth, PhosSepticLoad, PhosPlantUptake, Grow):
    result = np.zeros((NYrs,12))
    grow_factor = Grow_Factor.Grow_Factor(NYrs, DaysMonth, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = (result[Y][i] + PhosSepticLoad - PhosPlantUptake * grow_factor[i])
    return result


def MonthShortPhos_2():
    pass
