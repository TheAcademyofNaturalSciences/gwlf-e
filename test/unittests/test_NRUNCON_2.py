import numpy as np
from VariableUnittest import VariableUnitTest
from gwlfe.BMPs.AgAnimal import NRUNCON_2
from unittest import skip


class TestNRUNCON_2(VariableUnitTest):
    @skip('Not Ready Yet.')
    def test_NRUNCON_2(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            NRUNCON_2.NRUNCON_2_f(),
            NRUNCON_2.NRUNCON_2(), decimal=7)