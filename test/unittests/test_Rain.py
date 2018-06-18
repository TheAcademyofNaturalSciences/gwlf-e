import numpy as np

from VariableUnittest import VariableUnitTest
from gwlfe import Rain


class TestRain(VariableUnitTest):

    def test_Rain(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            Rain.Rain_f(z.Temp, z.Prec),
            Rain.Rain(z.NYrs, z.DaysMonth, z.Temp, z.Prec), decimal=7)
