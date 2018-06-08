import numpy as np
from gwlfe.Timer import time_function
from Precipitation import Precipitation
from Precipitation import Precipitation_2


def AvPrecipitation(NYrs, DaysMonth, Prec):
    result = np.zeros((12,))
    precipitation = Precipitation(NYrs, DaysMonth, Prec)
    for Y in range(NYrs):
        for i in range(12):
            result[i] += precipitation[Y][i] / NYrs
    return result


def AvPrecipitation_2(Prec):
    precipitation = Precipitation_2(Prec)
    return np.average(precipitation, axis=0)
