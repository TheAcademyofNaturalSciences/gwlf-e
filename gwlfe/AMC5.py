import numpy as np
from Timer import time_function
import Water

def AMC5(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist_initial):
    result = np.zeros((NYrs, 12, 31))
    AntMoist1 = np.zeros((5,))
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    AMC5 = 0
    for k in range(5):
        AMC5 += AntMoist_initial[k]
        AntMoist1[k] = AntMoist_initial[k]
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = AMC5
                AMC5 = AMC5 - AntMoist1[4] + water[Y][i][j]
                AntMoist1[4] = AntMoist1[3]
                AntMoist1[3] = AntMoist1[2]
                AntMoist1[2] = AntMoist1[1]
                AntMoist1[1] = AntMoist1[0]
                AntMoist1[0] = water[Y][i][j]
    return result


def AMC5_2():
    pass
