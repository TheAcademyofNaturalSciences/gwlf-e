import numpy as np
from Timer import time_function
import MonthDischargePhos
import MonthShortPhos
import MonthPondPhos

def DisSeptPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, NumShortSys, NumDischargeSys,PhosSepticLoad
                , PhosPlantUptake, Grow):
    result = np.zeros((NYrs, 12))

    monthdischargephos = MonthDischargePhos.MonthDischargePhos(NYrs, DaysMonth, PhosSepticLoad)
    monthshortphos = MonthShortPhos.MonthShortPhos(NYrs, DaysMonth, PhosSepticLoad, PhosPlantUptake, Grow)
    monthpondphos = MonthPondPhos.MonthPondPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, PhosSepticLoad
                                                , PhosPlantUptake, Grow)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (monthpondphos[Y][i] + monthshortphos[Y][i] * NumShortSys[i] + monthdischargephos[Y][i]
                     * NumDischargeSys[i])
            result[Y][i] = result[Y][i] / 1000
    return result


def DisSeptPhos_2():
    pass
