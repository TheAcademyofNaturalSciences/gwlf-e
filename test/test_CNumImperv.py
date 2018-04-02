import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import CNumImperv, gwlfe


class TestCNumImperv(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_CNumImperv(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.CNumImpervStorage,
            z.CNumImperv_isolate, decimal=7)



    # def test_CNumImperv2(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         CNumImperv.CNumImperv_2(),
    #         CNumImperv.CNumImperv(), decimal=7)