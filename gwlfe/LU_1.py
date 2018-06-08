import numpy as np
from Timer import time_function
from NLU_function import NLU_function
from Memoization import memoize


@memoize
def LU_1(NRur, NUrb):
    nlu = NLU_function(NRur, NUrb)
    result = np.zeros((nlu,)).astype("int")
    for l in range(NRur, nlu):
        result[l] = l - 11
    return result

#Tried, it was slower. LU_1 is faster
# def LU_1_2():
#     pass
