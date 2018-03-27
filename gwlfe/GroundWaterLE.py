# import numpy as np
# from Timer import time_function
#
# def GwAgLE(NYrs,AreaTotal,GroundWatLE,AgAreaTotal):
#     result = np.zeros((NYrs,12))
#     for Y in range(NYrs):
#         for i in range(12):
#             if AreaTotal > 0:
#                 result[Y][i] = (result[Y][i] + (GroundWatLE[Y][i] * (AgAreaTotal / AreaTotal)))
#     return result
#
# def GwAgLE_2():
#     pass
#
# def TileDrainGW(NYrs,GwAgLE,TileDrainDensity):
#     result = np.zeros((NYrs,12))
#     for Y in range(NYrs):
#         for i in range(12):
#             result[Y][i] = (result[Y][i] + [GwAgLE[Y][i] * TileDrainDensity])
#     return result
#
# def TileDrainGW_2():
#     pass
#
# def GroundWaterLE(NYrs,DaysMonth,GrFlow,GWAgLE,TileDrainDensity):
#     result = np.zeros((NYrs,12))
#     tileDrainGW = TileDrainGW(NYrs,GWAgLE,TileDrainDensity)
#     for Y in range(NYrs):
#         for i in range(12):
#             for j in range(DaysMonth[Y][i]):
#                 result[Y][i] = result[Y][i] + GrFlow
#                 # ADJUST THE GROUNDWATER FLOW
#                 result[Y][i] = result[Y][i] - tileDrainGW[Y][i]
#                 if result[Y][i] < 0:
#                     result[Y][i] = 0
#     return result
#
# def GroundWaterLE_2():
#     pass
#
# def GroundWatLETotal(NYrs,GroundWatLE):
#     result = 0
#     for Y in range(NYrs):
#         for i in range(12):
#             result += GroundWatLE[Y][i]
#         if result[Y] <= 0:
#             result[Y] = 0.0001
#
# def GroundWatLETotal_2():
#     pass