import numpy as np
from Timer import time_function
import AgRunoff

def TileDrainRO(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, Landuse, Area, TileDrainDensity):
    result = np.zeros((NYrs, 12))
    agrunoff= AgRunoff.AgRunoff(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            result[Y][i] = (result[Y][i] + [agrunoff[Y][i] * TileDrainDensity])
    return result

def TileDrainRO_2():
    pass
