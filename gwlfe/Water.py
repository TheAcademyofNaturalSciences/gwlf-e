import numpy as np
from Timer import time_function
import Rain
import InitSnow

def Water(NYrs, DaysMonth, Temp, Prec,InitialSnow):
    result = np.zeros((NYrs, 12, 31))
    rain = Rain.Rain(NYrs, DaysMonth, Temp, Prec)
    _, meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0:
                    pass
                else:
                    result[Y][i][j] = rain[Y][i][j] + meltpest[Y][i][j]
    return result


def Water_2():
    pass
