import numpy as np

from VariableUnittest import VariableUnitTest
from gwlfe import GrowFactor


class TestGrowFactor(VariableUnitTest):

    def test_GrowFactor(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            GrowFactor.GrowFactor_f(z.Grow_0),
            GrowFactor.GrowFactor(z.Grow_0), decimal=7)
