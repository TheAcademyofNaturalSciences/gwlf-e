import numpy as np
from Timer import time_function
import InitSnow
import PondPhosLoad

def FrozenPondPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow):
    result = np.zeros((NYrs,12,31))
    initsnow, meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    pondphosload = PondPhosLoad.PondPhosLoad(NYrs, DaysMonth, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0 or initsnow[Y][i][j] > 0:
                    result[Y][i][j] = result[Y][i][j] + pondphosload[Y][i][j]
                else:
                    result[Y][i][j] = 0
    return result



def FrozenPondPhos_2():
    pass
