import numpy as np
from Timer import time_function
import CNP
import NLU
import InitSnow
import Grow_Factor
import AMC5


def CNumPerv(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, cnp, NRur, NUrb, Grow):
    #cnp = CNP.CNP(NRur, NLU, Cnp)
    nlu = NLU.NLU(NRur, NUrb)
    _,meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    grow_factor = Grow_Factor.Grow_Factor(NYrs, DaysMonth, Grow)
    amc5 = AMC5.AMC5(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist)
    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, nlu):
                    if cnp[1][l] > 0:
                        if meltpest[Y][i][j] <= 0:
                            if grow_factor[i] > 0:
                                # Growing season
                                if amc5[Y][i][j] >= 5.33:
                                    result[Y][i][j][l] = cnp[2][l]
                                elif amc5[Y][i][j] < 3.56:
                                    result[Y][i][j][l] = cnp[0][l] + (cnp[1][l] - cnp[0][l]) * amc5[Y][i][j] / 3.56
                                else:
                                    result[Y][i][j][l] = cnp[1][l] + (cnp[2][l] - cnp[1][l]) * (amc5[Y][i][j] - 3.56) / 1.77
                            else:
                                # Dormant season
                                if amc5[Y][i][j] >= 2.79:
                                    result[Y][i][j][l] = cnp[2][l]
                                elif amc5[Y][i][j] < 1.27:
                                    result[Y][i][j][l] = cnp[0][l] + (cnp[1][l] - cnp[0][l]) * amc5[Y][i][j] / 1.27
                                else:
                                    result[Y][i][j][l] = cnp[1][l] + (cnp[2][l] - cnp[1][l]) * (amc5[Y][i][j] - 1.27) / 1.52
                        else:
                            result[Y][i][j][l] = cnp[2][l]
    return result


def CNumPerv_2():
    pass
