import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import GrowFactor


class TestGrowFactor(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    @skip("not ready")
    def test_GrowFactor(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            GrowFactor.GrowFactor_2(z.Grow),
            GrowFactor.GrowFactor(z.Grow), decimal=7)