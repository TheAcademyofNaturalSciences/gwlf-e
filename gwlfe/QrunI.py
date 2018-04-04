import numpy as np
from Timer import time_function
import CNI
import Water
import CNumImpervReten
from NLU import NLU


def QrunI(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cni, Grow):
    #cni = CNI.CNI(NRur, NLU, Cni)
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    cnumimpervreten = CNumImpervReten.CNumImpervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cni, Grow)
    nlu = NLU(NRur,NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, nlu):
                    result[Y][i][j][l] = 0
                for l in range(NRur, nlu):
                    if cni[1][l] > 0:
                        if water[Y][i][j] >= 0.2 * cnumimpervreten[Y][i][j][l]:
                            result[Y][i][j][l] = (water[Y][i][j] - 0.2 * cnumimpervreten[Y][i][j][l]) ** 2 / (water[Y][i][j] + 0.8 * cnumimpervreten[Y][i][j][l])

    return result

def QrunI_2():
    pass
