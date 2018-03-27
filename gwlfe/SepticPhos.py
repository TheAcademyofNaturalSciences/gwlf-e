import numpy as np
from Timer import time_function
import DisSeptPhos

def SepticPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, NumShortSys, NumDischargeSys, PhosSepticLoad
                , PhosPlantUptake, Grow):
    result = np.zeros((NYrs,))
    disseptphos = DisSeptPhos.DisSeptPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, NumShortSys, NumDischargeSys, PhosSepticLoad
                , PhosPlantUptake, Grow)
    for Y in range(NYrs):
        for i in range(12):
            result[Y] += disseptphos[Y][i]
    return result


def SepticPhos_2():
    pass
