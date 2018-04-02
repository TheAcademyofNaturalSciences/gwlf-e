import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import AMC5, gwlfe


class TestAMC5(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_AMC5_1(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.AMC5Storage,
            z.AMC5_isolate, decimal=7)


    # def test_AMC5_2(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         AMC5.AMC5_2(),
    #         AMC5.AMC5(), decimal=7)