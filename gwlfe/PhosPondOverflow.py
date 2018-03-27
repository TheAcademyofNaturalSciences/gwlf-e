import numpy as np
from Timer import time_function
import FrozenPondPhos
import PondPhosLoad
import InitSnow

def PhosPondOverflow(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow):
    result = np.zeros((NYrs,12,31))
    frozenpondphos = FrozenPondPhos.FrozenPondPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow)
    pondphosload = PondPhosLoad.PondPhosLoad(NYrs, DaysMonth, NumPondSys, PhosSepticLoad, PhosPlantUptake, Grow)
    initsnow,_ = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0 or initsnow[Y][i][j] > 0:
                    result[Y][i][j] = 0
                else:
                    result[Y][i][j] = frozenpondphos[Y][i][j] + pondphosload[Y][i][j]
    return result


def PhosPondOverflow_2():
    pass
