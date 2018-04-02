import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import CNumImpervReten, gwlfe


class TestCNumImpervReten(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    def test_CNumImpervReten(self):
        z = self.z
        _, z = gwlfe.run(z)
        np.testing.assert_array_almost_equal(
            z.CNumImpervRetenStorage,
            z.CNumImpervReten_isolate, decimal=7)


    # def test_CNumImpervReten(self):
    #     z = self.z
    #     np.testing.assert_array_almost_equal(
    #         CNumImpervReten.CNumImpervReten_2(),
    #         CNumImpervReten.CNumImpervReten(), decimal=7)