import numpy as np
from Timer import time_function
from numba import jit
from scipy.linalg import toeplitz


@time_function
def SatStor(NYrs, DaysMonth, Percolation, GrFlow, DeepSeep):
    result = np.zeros((NYrs, 12, 31))
    satStor = 0  # not necessarily true?
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satStor = satStor + Percolation[Y][i][j] - GrFlow[Y][i][j] - DeepSeep[Y][i][j]
                if satStor < 0:
                    satStor = 0
                result[Y][i][j] = satStor
    return result


def totalDays(DaysMonth):
    return np.sum(DaysMonth)


@time_function
def SatStor_1(NYrs, DaysMonth, Percolation, GrFlow, DeepSeep):
    N = totalDays(DaysMonth)
    k = 0
    result = np.zeros((N, 1))
    satStor = 0  # not necessarily true?
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satStor = satStor + Percolation[Y][i][j] - GrFlow[Y][i][j] - DeepSeep[Y][i][j]
                if satStor < 0:
                    satStor = 0
                result[k, 0] = satStor
                k += 1
    return result


def zeropad_sliding2D(a):
    L = a.size
    a_ext = np.concatenate((np.full(a.size - 1, 0.0), a))
    n = a_ext.strides[0]
    strided = np.lib.stride_tricks.as_strided
    return np.fliplr(strided(a_ext, shape=(L, L), strides=(n, n)))


@time_function
def makeA(recessionCoef, seepCoef, n):
    return zeropad_sliding2D((1 - recessionCoef - seepCoef) ** (np.arange(n).reshape(n)))


@time_function
def makeB(recessionCoef, seepCoef, n):
    return (1 - recessionCoef - seepCoef) ** (np.arange(n).reshape(n, 1) + 1)


@time_function
def satStor(A, B, satstor0, Percolation):
    return np.dot(A, Percolation)


def SatStor_2(DaysMonth, Percolation, recessionCoef, seepCoef, satstor0):
    n = totalDays(DaysMonth)
    A = makeA(recessionCoef, seepCoef, n)
    # A_matrix = np.fliplr(toeplitz(A, np.full(A.size,0.0) )[:,::-1]) #or A_matrix = zeropad_sliding2D(A)
    # A_matrix = zeropad_sliding2D(A)
    B = makeB(recessionCoef, seepCoef, n)
    if (recessionCoef + seepCoef < 1):
        satstor = satStor(A, B, satstor0, Percolation)
    return satstor
    # else:
    #    satstor = B * satstor0 + np.dot(A_matrix, Perc.reshape(n, 1)) - ...


@time_function
@jit(cache=True, nopython=True)
def SatStor_3(NYrs, DaysMonth, Percolation, GrFlow, DeepSeep):
    result = np.zeros((NYrs, 12, 31))
    satStor = 0  # not necessarily true?
    for Y in range(NYrs):
        for i in range(12):
            for j in range(DaysMonth[Y][i]):
                satStor = satStor + Percolation[Y][i][j] - GrFlow[Y][i][j] - DeepSeep[Y][i][j]
                if satStor < 0:
                    satStor = 0
                result[Y][i][j] = satStor
    return result


@time_function
@jit(cache=True, nopython=True)
def test(Percolation, GrFlow, DeepSeep):
    satStor = 0
    result = np.zeros_like(Percolation)
    for i in range(0, len(Percolation)):
        satStor = satStor + Percolation[i] - GrFlow[i] - DeepSeep[i]
        if satStor < 0:
            satStor = 0
        result[i] = satStor
    return result


def SatStor_4(NYrs, DaysMonth, Percolation, GrFlow, DeepSeep):
    result = np.zeros((NYrs, 12, 31))
    satStor = 0  # not necessarily true?
    percolation = np.ravel(Percolation)
    grflow = np.ravel(GrFlow)
    deepseep = np.ravel(DeepSeep)
    return test(percolation, grflow, deepseep)


def SatStor_5(Percolation, GrFlow, DeepSeep, n):
    satStor = np.zeros(n);
    satStor[0] = np.maximum(np.subtract(np.add(satStor[0], Percolation[0]), np.add(GrFlow[0], DeepSeep[0])), 0)
    satStor[1:(n - 1):1] = np.maximum(np.subtract(np.add(satStor[0:(n - 2):1], Percolation[1:(n - 1):1]),
                                                  np.add(GrFlow[1:(n - 1):1], DeepSeep[1:(n - 1):1])), 0)
    return satStor


@time_function
def SatStor_4(Percolation, GrFlow, DeepSeep, n):
    satStor = np.zeros(n);
    satStor[0] = np.maximum(np.subtract(np.add(satStor[0], Percolation[0]), np.add(GrFlow[0], DeepSeep[0])), 0)
    satStor[1:(n - 1):1] = np.maximum(np.subtract(np.add(satStor[0:(n - 2):1], Percolation[1:(n - 1):1]),
                                                  np.add(GrFlow[1:(n - 1):1], DeepSeep[1:(n - 1):1])), 0)
    return satStor

@time_function
@jit(cache=True, nopython=True)
def SatStor_6(SatStor_0,Percolation, RecessionFactor, SeepCoef):
    result = np.copy(Percolation)
    reduction = (1 - RecessionFactor - SeepCoef)
    result[0] += SatStor_0 * reduction
    for i in range(1, len(result)):
        result[i] += result[i - 1] * reduction
    return result

@time_function
@jit(cache=True, nopython=True)
def SatStor_7(Percolation, RecessionFactor, SeepCoef):
    reduction = (1 - RecessionFactor) * (1 - SeepCoef)
    sat_ufunc = np.frompyfunc(lambda x, y: (x * reduction ) + (y * reduction ) ,  2, 1) 
    return sat_ufunc.accumulate(Percolation,dtype=np.object).astype(np.float)





