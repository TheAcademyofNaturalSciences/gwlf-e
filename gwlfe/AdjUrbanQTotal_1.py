from numpy import where
from numpy import zeros

# from Timer import time_function
from AdjUrbanQTotal import AdjUrbanQTotal
from AdjUrbanQTotal import AdjUrbanQTotal_f
from AreaTotal import AreaTotal
from AreaTotal import AreaTotal_f
from Memoization import memoize
from UrbAreaTotal import UrbAreaTotal
from UrbAreaTotal import UrbAreaTotal_f
from Water import Water
from Water import Water_f


@memoize
def AdjUrbanQTotal_1(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                     Imper, ISRR, ISRA, Qretention, PctAreaInfil):
    result = zeros((NYrs, 12, 31))
    adj_urban_q_total = AdjUrbanQTotal(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0,
                                       Grow_0, CNP_0, Imper,
                                       ISRR, ISRA, Qretention, PctAreaInfil)
    urb_area_total = UrbAreaTotal(NRur, NUrb, Area)
    area_total = AreaTotal(NRur, NUrb, Area)
    water = Water(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                if Temp[Y][i][j] > 0 and water[Y][i][j] > 0.01:
                    # result[Y][i][j] = adj_urban_q_total[Y][i][j] * area_total / urb_area_total
                    if urb_area_total > 0:
                        result[Y][i][j] = adj_urban_q_total[Y][i][j] * urb_area_total / area_total
                    else:
                        # adj_urban_q_total = 0
                        result[Y][i][j] = 0
                    # TODO: when I broke this cycle, the only way I could think to do this was to undo the calculation done at the end of adj_urban_q_total. Hopefully there is a better way
    return result

@memoize
def AdjUrbanQTotal_1_f(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0,
                     Imper, ISRR, ISRA, Qretention, PctAreaInfil):
    result = zeros((NYrs, 12, 31))
    adj_urban_q_total = AdjUrbanQTotal_f(NYrs, DaysMonth, Temp, InitSnow_0, Prec, NRur, NUrb, Area, CNI_0, AntMoist_0, Grow_0, CNP_0, Imper,
                   ISRR, ISRA, Qretention, PctAreaInfil)
    urb_area_total = UrbAreaTotal_f(NRur,NUrb,Area)
    area_total = AreaTotal_f(Area)
    water = Water_f(NYrs, DaysMonth, InitSnow_0, Temp, Prec)
    result[where((Temp >0) & (water > 0.01))] = adj_urban_q_total[where((Temp >0) & (water > 0.01))] *  urb_area_total / area_total
    return result