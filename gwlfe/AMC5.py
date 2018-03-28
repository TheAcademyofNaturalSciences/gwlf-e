import numpy as np
from Timer import time_function
import Water

def AMC5(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist):
    result = np.zeros((NYrs, 12, 31))
    water = Water.Water(NYrs, DaysMonth, Temp, Prec,InitialSnow)
    AMC5 = 0
    for k in range(5):
        AMC5 += AntMoist[k]
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = AMC5
                AMC5 = AMC5 - AntMoist[4] + water[Y][i][j]
                AntMoist[4] = AntMoist[3]
                AntMoist[3] = AntMoist[2]
                AntMoist[2] = AntMoist[1]
                AntMoist[1] = AntMoist[0]
                AntMoist[0] = water[Y][i][j]
    return result


def AMC5_2():
    pass
