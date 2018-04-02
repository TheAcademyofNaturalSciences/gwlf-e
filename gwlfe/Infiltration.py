import numpy as np
from Timer import time_function
import Water
import QTotal

def Infiltration():
    result = np.zeros((NYrs, 12, 31))
    qtotal = QTotal.QTotal()
    water = Water.Water(NYrs, DaysMonth, Temp, Prec,InitialSnow)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if qtotal[Y][i][j] <= water[Y][i][j]:
                    result[Y][i][j] = water[Y][i][j] - qtotal[Y][i][j]
    return result


def Infiltration_2():
    pass
