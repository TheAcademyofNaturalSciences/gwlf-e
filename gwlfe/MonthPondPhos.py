import numpy as np
from Timer import time_function
import PhosPondOverflow

def MonthPondPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow):
    result = np.zeros((NYrs,12))
    phospondoverflow = PhosPondOverflow.PhosPondOverflow(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + phospondoverflow[Y][i][j]
    return result


def MonthPondPhos_2():
    pass
