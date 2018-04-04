import numpy as np
from Timer import time_function
import CNI
#import NLU
import InitSnow
import Grow_Factor
import AMC5
from NLU import NLU


def CNumImperv(NYrs, DaysMonth, NRur, NUrb, cni, Temp, Prec, InitialSnow, AntMoist_initial, Grow):
    nlu = NLU(NRur, NUrb)
    # cni = CNI.CNI(NRur, nlu, _cni)
    _,meltpest = InitSnow.InitSnow(NYrs, DaysMonth, Temp, Prec, InitialSnow)
    grow_factor = Grow_Factor.Grow_Factor(NYrs, DaysMonth, Grow)
    amc5 = AMC5.AMC5(NYrs, DaysMonth, Temp, Prec, InitialSnow, AntMoist_initial)

    result = np.zeros((NYrs, 12, 31, nlu))
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                for l in range(NRur, nlu):
                    if cni[1][l] > 0:
                        if meltpest[Y][i][j] <= 0:
                            if grow_factor[i] > 0:
                                # Growing season
                                if amc5[Y][i][j] >= 5.33:
                                    result[Y][i][j][l] = cni[2][l]
                                elif amc5[Y][i][j] < 3.56:
                                    result[Y][i][j][l] = cni[0][l] + (cni[1][l] - cni[0][l]) * amc5[Y][i][j] / 3.56
                                else:
                                    result[Y][i][j][l] = cni[1][l] + (cni[2][l] - cni[1][l]) * (amc5[Y][i][j] - 3.56) / 1.77
                            else:
                                # Dormant season
                                if amc5[Y][i][j] >= 2.79:
                                    result[Y][i][j][l] = cni[2][l]
                                elif amc5[Y][i][j] < 1.27:
                                    result[Y][i][j][l] = cni[0][l] + (cni[1][l] - cni[0][l]) * amc5[Y][i][j] / 1.27
                                else:
                                    result[Y][i][j][l] = cni[1][l] + (cni[2][l] - cni[1][l]) * (amc5[Y][i][j] - 1.27) / 1.52
                        else:
                            result[Y][i][j][l] = cni[2][l]
    return result


def CNumImperv_2():
    pass
    # for l in range(z.NRur, z.NLU):
    #     #grow_factor = GrowFlag.intval(z.Grow[i])
    #
    #     # Find curve number
    #     if z.CNI[1][l] > 0:
    #         if z.MeltPest[Y][i][j] <= 0:
    #             if z.Grow_Factor[i] > 0:
    #                 # Growing season
    #                 if z.AMC5Storage[Y][i][j] >= 5.33:
    #                     z.CNumImperv = z.CNI[2][l]
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #                 elif z.AMC5Storage[Y][i][j] < 3.56:
    #                     z.CNumImperv = z.CNI[0][l] + (z.CNI[1][l] - z.CNI[0][l]) * z.AMC5Storage[Y][i][j] / 3.56
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #                 else:
    #                     z.CNumImperv = z.CNI[1][l] + (z.CNI[2][l] - z.CNI[1][l]) * (z.AMC5Storage[Y][i][j] - 3.56) / 1.77
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #             else:
    #                 # Dormant season
    #                 if z.AMC5Storage[Y][i][j] >= 2.79:
    #                     z.CNumImperv = z.CNI[2][l]
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #                 elif z.AMC5Storage[Y][i][j] < 1.27:
    #                     z.CNumImperv = z.CNI[0][l] + (z.CNI[1][l] - z.CNI[0][l]) * z.AMC5Storage[Y][i][j] / 1.27
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #                 else:
    #                     z.CNumImperv = z.CNI[1][l] + (z.CNI[2][l] - z.CNI[1][l]) * (z.AMC5Storage[Y][i][j] - 1.27) / 1.52
    #                     z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv
    #         else:
    #             z.CNumImperv = z.CNI[2][l]
    #             z.CNumImpervStorage[Y][i][j][l] = z.CNumImperv