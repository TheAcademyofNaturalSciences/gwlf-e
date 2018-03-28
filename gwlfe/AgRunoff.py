import numpy as np
from Timer import time_function
import AgQTotal

def AgRunoff(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, Landuse, Area):
    result = np.zeros((NYrs, 12))
    agqtotal = AgQTotal.AgQTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] += agqtotal[Y][i][j]
    return result

def AgRunoff_2():
    pass
