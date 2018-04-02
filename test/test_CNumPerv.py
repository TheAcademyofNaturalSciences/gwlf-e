import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import CNumPerv, gwlfe


class TestCNumPerv(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_CNumPerv(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.CNumPervStorage,
            z.CNumPerv_isolate, decimal=7)

    # def test_CNumPerv(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         CNumPerv.CNumPerv_2(),
    #         CNumPerv.CNumPerv(), decimal=7)