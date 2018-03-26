import numpy as np
from Timer import time_function
import InitSnow

def FrozenPondPhos(NYrs, DaysMonth, Temp, Prec, InitialSnow):
    result = np.zeros((NYrs,12,31))
    initsnow, meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] <= 0 or initsnow[Y][i][j] > 0:
    pass



def FrozenPondPhos_2():
    pass
