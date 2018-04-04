import numpy as np
from Timer import time_function
from NLU import NLU
import CNP
import CNumPerv


def CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, cnp, Grow):
    #cnp = CNP.CNP(NRur, NLU, Cnp)
    cnumperv = CNumPerv.CNumPerv(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, cnp, NRur, NUrb, Grow)
    nlu = NLU(NRur, NUrb)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, nlu):
                    if cnp[1][l] > 0:
                        result[Y][i][j][l] = 2540 / cnumperv[Y][i][j][l] - 25.4
                        if result[Y][i][j][l] < 0:
                            result[Y][i][j][l] = 0
    return result

def CNumPervReten_2():
    pass
