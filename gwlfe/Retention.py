import numpy as np
from Timer import time_function
import CNum

def Retention(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow):
    result = np.zeros((NYrs, 12, 31, NRur))
    cnum = CNum.CNum(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if CN[l] > 0:
                        result[Y][i][j][l] = 2540 / cnum[Y][i][j][l] - 25.4
                        if result[Y][i][j][l] < 0:
                            result[Y][i][j][l] = 0
    return result

def Retention_2():
    pass
