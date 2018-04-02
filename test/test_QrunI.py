import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import QrunI, gwlfe


class TestQrunI(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_QrunI(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.QrunIStorage,
            z.QrunI_isolate, decimal=7)

    # def test_QrunI2(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         QrunI.QrunI_2(),
    #         QrunI.QrunI(), decimal=7)