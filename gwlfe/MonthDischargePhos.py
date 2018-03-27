import numpy as np
from Timer import time_function


def MonthDischargePhos(NYrs, DaysMonth, PhosSepticLoad):
    result = np.zeros((NYrs,12))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                result[Y][i] = result[Y][i] + PhosSepticLoad
    return result


def MonthDischargePhos_2():
    pass
