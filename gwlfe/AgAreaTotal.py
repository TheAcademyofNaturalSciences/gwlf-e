import numpy as np
from Timer import time_function
from enums import LandUse
from Memoization import memoize


# @memoize
def AgAreaTotal(NRur, Landuse_2, Area):
    result = 0
    for l in range(NRur):
        if Landuse_2[l] is LandUse.FOREST:
            pass
        elif Landuse_2[l] is LandUse.CROPLAND:
            result += Area[l]
        elif Landuse_2[l] is LandUse.HAY_PAST:
            result += Area[l]
        elif Landuse_2[l] is LandUse.TURFGRASS:
            result += Area[l]
    return result

# vectorization is slower
# @time_function
# def AgAreaTotal_2(Landuse, Area):
#     return Area[Landuse == LandUseNames.CROPLAND] + \
#            Area[Landuse == LandUseNames.HAY_PAST] + \
#            Area[Landuse == LandUseNames.TURFGRASS]
