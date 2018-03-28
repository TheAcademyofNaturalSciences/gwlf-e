import numpy as np
from Timer import time_function
#import NLU
import CNI
import CNumImperv


def CNumImpervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NLU, Cni, Grow):
    #nlu = NLU.NLU(NRur, NUrb)
    cni = CNI.CNI(NRur, NLU, Cni)
    cnumimperv = CNumImperv.CNumImperv(NYrs, DaysMonth, NRur, NLU, Cni, Temp, Prec, InitialSnow, AntMoist, Grow)
    result = np.zeros((NYrs, 12, 31, NLU))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, NLU):
                    if cni[1][l] > 0:
                        result[Y][i][j][l] = 2540 / cnumimperv[Y][i][j][l] - 25.4
                        if result[Y][i][j][l] < 0:
                            result[Y][i][j][l] = 0
    return result


def CNumImpervReten_2():
    pass
