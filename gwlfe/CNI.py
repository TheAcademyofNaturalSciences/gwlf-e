import numpy as np
from Timer import time_function


def CNI(NRur, NLU, CNI):
    #nlu = NLU.NLU(NRur, NUrb)
    for l in range(NRur, NLU):
        CNI[0][l] = CNI[1][l] / (2.334 - 0.01334 * CNI[1][1])
        CNI[2][l] = CNI[1][l] / (0.4036 + 0.0059 * CNI[1][l])
    return CNI


def CNI_2():
    pass
