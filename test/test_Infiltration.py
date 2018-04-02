import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import Infiltration


class TestInfilteration(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    def test_Infilteration(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            Infiltration.Infilteration_2(),
            Infiltration.Infilteration(), decimal=7)