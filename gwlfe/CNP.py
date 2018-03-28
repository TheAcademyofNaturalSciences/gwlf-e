import numpy as np
from Timer import time_function


def CNP(NRur, NLU, CNP):
    #nlu = NLU.NLU(NRur, NUrb)
    for l in range(NRur, NLU):
        CNP[0][l] = CNP[1][l] / (2.334 - 0.01334 * CNP[1][1])
        CNP[2][l] = CNP[1][l] / (0.4036 + 0.0059 * CNP[1][l])
    return CNP


def CNP_2():
    pass
