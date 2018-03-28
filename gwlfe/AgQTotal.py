import numpy as np
from Timer import time_function
import Water
import Retention
import Qrun
from .enums import LandUse
import AgAreaTotal


def AgQTotal(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow, Landuse, Area):
    result = np.zeros((NYrs, 12, 31))
    water = Water.Water(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    retention = Retention.Retention(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    qrun = Qrun.Qrun(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist, CN, NRur, NUrb, Grow)
    agareatotal = AgAreaTotal.AgAreaTotal(NRur, Landuse, Area)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur):
                    if CN[l] > 0:
                        if water[Y][i][j] >= 0.2 * retention[Y][i][j][l]:
                            if Landuse[l] is LandUse.CROPLAND:
                                # (Maybe used for STREAMPLAN?)
                                result[Y][i][j] += qrun[Y][i][j][l] * Area[l]
                                # z.AgQRunoff[l][i] += z.Qrun
                            elif Landuse[l] is LandUse.HAY_PAST:
                                result[Y][i][j] += qrun[Y][i][j][l] * Area[l]
                                # z.AgQRunoff[l][i] += z.Qrun
                            elif Landuse[l] is LandUse.TURFGRASS:
                                result[Y][i][j] += qrun[Y][i][j][l] * Area[l]
                if agareatotal > 0:
                    result[Y][i][j] = result[Y][i][j] / agareatotal
                else:
                    result[Y][i][j] = 0
    return result

def AgQTotal_2():
    pass
