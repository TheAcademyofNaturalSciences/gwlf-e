import numpy as np
from Timer import time_function

def Percolation(NYrs,DaysMonth,MaxWaterCap):
   result = np.zeros((NYrs,12,31))
   percolation = 0
   for Y in range(NYrs):
      for i in range(12):
         for j in range(DaysMonth[Y][i]):
            # CALCULATE EVAPOTRANSPIRATION, Percolation, AND THE
            # NEXT DAY'S UNSATURATED STORAGE AS LIMITED BY THE UNSATURATED
            # ZONE MAXIMUM WATER CAPACITY

            z.UnsatStor = z.UnsatStor + z.Infiltration

            # Calculate water balance for non-Pesticide componenets
            if z.ET >= z.UnsatStor:
               z.ET = z.UnsatStor
               z.UnsatStor = 0
            else:
               z.UnsatStor = z.UnsatStor - z.ET

            # Obtain the Percolation, adjust precip and UnsatStor values
            if UnsatStor > MaxWaterCap:
               percolation = UnsatStor - MaxWaterCap
               result[Y][i][j] = UnsatStor - MaxWaterCap
               z.UnsatStor = z.UnsatStor - percolation
            else:
               percolation = 0
               result[Y][i][j] = 0
            z.SatStor = z.SatStor + percolation - z.GrFlow - z.DeepSeep
            if z.SatStor < 0:
               z.SatStor = 0
   return result

def Percolation_2():
   pass

def PercCM(NYrs,DaysMonth,Percolation):
   result = np.zeros((NYrs, 12, 31))
   for Y in range(NYrs):
      for i in range(12):
         for j in range(DaysMonth[Y][i]):
            result[Y][i][j] = Percolation[Y][i][j] / 100
   return result

def PercCM_2(NYrs,DaysMonth,Percolation):
   pass