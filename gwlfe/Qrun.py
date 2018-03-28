import numpy as np
from Timer import time_function
import Water
import Retention


def Qrun(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow):
    result = np.zeros((NYrs, 12, 31, NRur))
    water = Water.Water(NYrs, DaysMonth, Temp, Prec,InitialSnow)
    retention = Retention.Retention(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if CN[l] > 0:
                        if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                            result[Y][i][j][l] = (water[Y][i][j] - 0.2 * retention[Y][i][j][l]) ** 2 / (
                                        water[Y][i][j] + 0.8 * retention[Y][i][j][l])
                        else:
                            result[Y][i][j][l] = 0
    return result


def Qrun_2():
    pass
