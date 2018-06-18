import numpy as np

from VariableUnittest import VariableUnitTest
from gwlfe import Water


class TestWater(VariableUnitTest):

    def test_Water_ground_truth(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            np.load("unittests/Water.npy"),
            Water.Water(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec), decimal=7)

    def test_Water(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            Water.Water_f(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec),
            Water.Water(z.NYrs, z.DaysMonth, z.InitSnow_0, z.Temp, z.Prec), decimal=7)
