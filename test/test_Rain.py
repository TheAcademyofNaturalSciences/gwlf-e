import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import Rain, gwlfe


class TestRain(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_Rain1(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.Rain,
            z.Rain_isolate, decimal=7)

    # def test_Rain(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         Rain.Rain_2(),
    #         Rain.Rain(), decimal=7)