import numpy as np
from Timer import time_function
import CNP
import Water
import CNumPervReten
from NLU import NLU


def QrunP(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cnp, Grow):
    #cnp = CNP.CNP(NRur, NLU, Cnp)
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    cnumpervreten = CNumPervReten.CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cnp, Grow)
    nlu = NLU(NRur,NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, nlu):
                    result[Y][i][j][l] = 0
                for l in range(NRur, nlu):
                    if cnp[1][l] > 0:
                        if water[Y][i][j] >= 0.2 * cnumpervreten[Y][i][j][l]:
                            result[Y][i][j][l] = (water[Y][i][j] - 0.2 * cnumpervreten[Y][i][j][l]) ** 2 / (water[Y][i][j] + 0.8 * cnumpervreten[Y][i][j][l])
    return result


def QrunP_2():
    pass
