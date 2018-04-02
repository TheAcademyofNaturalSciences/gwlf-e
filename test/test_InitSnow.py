import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import InitSnow, gwlfe


class TestInitSnow(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    def test_InitSnow(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.MeltPest_isolate,
            z.MeltPest, decimal=7)


    #
    # def test_InitSnow2(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         InitSnow.InitSnow_2(),
    #         InitSnow.InitSnow(), decimal=7)