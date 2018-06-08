# from numba.pycc import CC
import numpy as np
from gwlfe import cc
# cc = CC('DeepSeep_inner_compiled')


@cc.export('DeepSeep_inner', '(int64, float64, int32[:,::1], float64, float64, float64[:,:,::1])')
def DeepSeep_inner(NYrs, SatStor_0, DaysMonth, RecessionCoef, SeepCoef, percolation):
    deepseep = np.zeros((NYrs, 12, 31))
    grflow = np.zeros((NYrs, 12, 31))
    satstor = np.zeros((NYrs, 12, 31))
    satstor_carryover = SatStor_0
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satstor[Y][i][j] = satstor_carryover
                grflow[Y][i][j] = RecessionCoef * satstor[Y][i][j]
                deepseep[Y][i][j] = SeepCoef * satstor[Y][i][j]
                satstor[Y][i][j] = satstor[Y][i][j] + percolation[Y][i][j] - grflow[Y][i][j] - deepseep[Y][i][j]
                if satstor[Y][i][j] < 0:
                    satstor[Y][i][j] = 0
                satstor_carryover = satstor[Y][i][j]
    return deepseep, grflow, satstor
