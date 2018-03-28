import numpy as np
from Timer import time_function
import CNP
import Water
import CNumPervReten


def QrunP(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, Cnp, Grow):
    cnp = CNP.CNP(NRur, NLU, Cnp)
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    cnumpervreten = CNumPervReten.CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, Cnp, Grow)
    result = np.zeros((NYrs, 12, 31, NLU))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, NLU):
                    result[Y][i][j][l] = 0
                for l in range(NRur, NLU):
                    if cnp[1][l] > 0:
                        if water[Y][i][j] >= 0.2 * cnumpervreten[Y][i][j][l]:
                            result[Y][i][j][l] = (water[Y][i][j] - 0.2 * cnumpervreten[Y][i][j][l]) ** 2 / (water[Y][i][j] + 0.8 * cnumpervreten[Y][i][j][l])
    return result


def QrunP_2():
    pass
