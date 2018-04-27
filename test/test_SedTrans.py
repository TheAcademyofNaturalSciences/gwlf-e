import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import SedTrans


class TestSedTrans(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    @skip('Not Ready Yet.')
    def test_SedTrans(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            SedTrans.SedTrans_2(),
            SedTrans.SedTrans(), decimal=7)