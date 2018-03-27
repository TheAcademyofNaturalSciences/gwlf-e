import numpy as np
from Timer import time_function
import SepticPhos


def AvSeptPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, NumShortSys, NumDischargeSys, PhosSepticLoad
               , PhosPlantUptake, Grow):
    result = 0.
    septicphos = SepticPhos.SepticPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow, NumPondSys, NumShortSys
            , NumDischargeSys, PhosSepticLoad
               , PhosPlantUptake, Grow)
    for Y in range(NYrs):
        result += septicphos[Y] / NYrs
    return result


def AvSeptPhos_2():
    pass
