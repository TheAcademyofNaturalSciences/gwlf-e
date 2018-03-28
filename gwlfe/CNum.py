import numpy as np
from Timer import time_function
import InitSnow
import NewCN
import AMC5
import Grow_Factor


def CNum(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow):
    _,meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    newcn = NewCN.NewCN(CN, NRur, NUrb)
    amc5 = AMC5.AMC5(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist)
    grow_factor = Grow_Factor.Grow_Factor(NYrs, DaysMonth, Grow)
    result = np.zeros((NYrs, 12, 31, NRur))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if CN[l] > 0:
                        if meltpest[Y][i][j] <= 0:
                            if grow_factor[i] > 0:
                                # growing season
                                if amc5[Y][i][j] >= 5.33:
                                    result[Y][i][j][l] = newcn[2][l]
                                elif amc5[Y][i][j] < 3.56:
                                    result[Y][i][j][l] = newcn[0][l] + (CN[l] - newcn[0][l]) * amc5[Y][i][j] / 3.56
                                else:
                                    result[Y][i][j][l] = CN[l] + (newcn[2][l] - CN[l]) * (amc5[Y][i][j] - 3.56) / 1.77
                            else:
                                # dormant season
                                if amc5[Y][i][j] >= 2.79:
                                    result[Y][i][j][l] = newcn[2][l]
                                elif amc5[Y][i][j] < 1.27:
                                    result[Y][i][j][l] = newcn[0][l] + (CN[l] - newcn[0][l]) * amc5[Y][i][j] / 1.27
                                else:
                                    result[Y][i][j][l] = CN[l] + (newcn[2][l] - CN[l]) * (amc5[Y][i][j] - 1.27) / 1.52
                        else:
                            result[Y][i][j][l] = newcn[2][l]
    return result
def CNum_2():
    pass
