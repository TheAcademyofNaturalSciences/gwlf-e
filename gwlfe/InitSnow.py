import numpy as np
from Timer import time_function


def InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow):
    result = np.zeros((NYrs, 12, 31))
    MeltPest = np.zeros((NYrs, 12, 31))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0:
                    result[Y][i][j] = InitialSnow + Prec[Y][i][j]
                    InitialSnow = result[Y][i][j]
                else:
                    if InitialSnow > 0.001:
                        Melt = 0.45 * Temp[Y][i][j]
                        MeltPest[Y][i][j] = Melt
                        if Melt > InitialSnow:
                            Melt = InitialSnow
                            MeltPest[Y][i][j] = InitialSnow
                        InitialSnow = InitialSnow - Melt
                        result[Y][i][j] = InitialSnow
                    else:
                        MeltPest[Y][i][j] = 0
    return result, MeltPest



def InitSnow_2():
    pass
