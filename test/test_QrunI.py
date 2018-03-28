import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import QrunI


class TestQrunI(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    def test_QrunI(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            QrunI.QrunI_2(),
            QrunI.QrunI(), decimal=7)