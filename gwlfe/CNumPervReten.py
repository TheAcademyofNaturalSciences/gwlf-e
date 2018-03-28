import numpy as np
from Timer import time_function
import NLU
import CNP
import CNumPerv


def CNumPervReten(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, NRur, NUrb, Cnp, Grow):
    nlu = NLU.NLU(NRur, NUrb)
    cnp = CNP.CNP(NRur, NUrb, Cnp)
    cnumperv = CNumPerv.CNumPerv(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, Cnp, NRur, NUrb, Grow)
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
