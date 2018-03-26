import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import Grow_Factor


class TestGrow_Factor(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    def test_Grow_Factor(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            Grow_Factor.Grow_Factor_2(),
            Grow_Factor.Grow_Factor(), decimal=7)