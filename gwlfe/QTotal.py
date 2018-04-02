import numpy as np
from Timer import time_function
import RuralQTotal
import AgQTotal
def QTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, RurAreaTotal, Area, AreaTotal):
    result = np.zeros((NYrs, 12, 31))
    urbanqtotal =
    ruralqtotal = RuralQTotal.RuralQTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NLU, Grow, RurAreaTotal, Area, AreaTotal)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i][j] = urbanqtotal[Y][i][j] + ruralqtotal[Y][i][j]
    return result

def QTotal_2():
    pass
