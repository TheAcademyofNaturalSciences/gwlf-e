import numpy as np
from Timer import time_function
from Memoization import memoize
from NLU_function import NLU_function
from LuTotNitr import LuTotNitr
from LuTotNitr import LuTotNitr_2
from RetentFactorN import RetentFactorN
from AttenN import AttenN


def LuTotNitr_1(NYrs, NRur, NUrb, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, CN, Grow_0,
                Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, CNP_0, Imper, ISRR, ISRA,
                Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed, FilterWidth, PctStrmBuf, Acoef,
                CNI_0, Nqual, ShedAreaDrainLake, RetentNLake, AttenFlowDist, AttenFlowVel, AttenLossRateN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, nlu))
    lu_tot_nitr = LuTotNitr(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                            Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                            FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, CNP_0, Imper,
                            ISRR, ISRA, Qretention, PctAreaInfil, LoadRateImp, LoadRatePerv, Storm, UrbBMPRed,
                            FilterWidth, PctStrmBuf, Acoef, CNI_0, Nqual)
    retent_factor_n = RetentFactorN(ShedAreaDrainLake, RetentNLake)
    atten_n = AttenN(AttenFlowDist, AttenFlowVel, AttenLossRateN)
    for y in range(NYrs):
        for l in range(nlu):
            result[y][l] = round((lu_tot_nitr[y][l] * retent_factor_n * (1 - atten_n)))
    return result


@memoize
def LuTotNitr_1_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0, Area, NitrConc, ManNitr,
                  ManuredAreas, FirstManureMonth, LastManureMonth, FirstManureMonth2, LastManureMonth2, SedDelivRatio_0,
                  KF, LS, C, P, SedNitr, Acoef, ShedAreaDrainLake, RetentNLake, AttenFlowDist, AttenFlowVel,
                  AttenLossRateN):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((NYrs, nlu))
    lu_tot_nitr = LuTotNitr_2(NYrs, DaysMonth, InitSnow_0, Temp, Prec, AntMoist_0, NRur, NUrb, CN, Grow_0,
                              Area, NitrConc, ManNitr, ManuredAreas, FirstManureMonth, LastManureMonth,
                              FirstManureMonth2, LastManureMonth2, SedDelivRatio_0, KF, LS, C, P, SedNitr, Acoef)
    retent_factor_n = RetentFactorN(ShedAreaDrainLake, RetentNLake)
    atten_n = AttenN(AttenFlowDist, AttenFlowVel, AttenLossRateN)
    # TODO: this is only a temporary fix until WriteOutputfiles has been fully extracted
    result[:, :NRur] = np.round((lu_tot_nitr * retent_factor_n * (1 - atten_n)))
    return result
