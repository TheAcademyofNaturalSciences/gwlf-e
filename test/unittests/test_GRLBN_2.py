import numpy as np
from VariableUnittest import VariableUnitTest
from gwlfe.AFOS.GrazingAnimals.Losses import GRLBN_2
from unittest import skip


class TestGRLBN_2(VariableUnitTest):
    @skip('Not Ready Yet.')
    def test_GRLBN_2(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            GRLBN_2.GRLBN_2_f(),
            GRLBN_2.GRLBN_2(), decimal=7)