import numpy as np
from Timer import time_function
from .enums import ETflag, GrowFlag

def Grow_Factor(NYrs, DaysMonth, Grow):
    result = np.zeros((12,))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[i] = GrowFlag.intval(Grow[i])
    return result

def Grow_Factor_2():
    pass
