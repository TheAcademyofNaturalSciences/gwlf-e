import numpy as np

from VariableUnittest import VariableUnitTest
from gwlfe import GroundWatLE_1
from gwlfe import Parser


class TestGroundWatLE_1(VariableUnitTest):
    def setUp(self):
        input_file = open('unittests/input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_GroundWatLE_1_ground_truth(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            np.load("unittests/GroundWatLE_1.npy"),
            GroundWatLE_1.GroundWatLE_1_f(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                          z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                          z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                          z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                          z.Landuse, z.TileDrainDensity), decimal=7)

    def test_GroundWatLE_1(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            GroundWatLE_1.GroundWatLE_1_f(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                          z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                          z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                          z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                          z.Landuse, z.TileDrainDensity),
            GroundWatLE_1.GroundWatLE_1(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area,
                                        z.CNI_0, z.AntMoist_0, z.Grow_0, z.CNP_0, z.Imper,
                                        z.ISRR, z.ISRA, z.CN, z.UnsatStor_0, z.KV, z.PcntET, z.DayHrs, z.MaxWaterCap,
                                        z.SatStor_0, z.RecessionCoef, z.SeepCoef,
                                        z.Landuse, z.TileDrainDensity), decimal=7)