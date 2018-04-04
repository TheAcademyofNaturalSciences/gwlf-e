import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import CNP


class TestCNP(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    @skip("not ready")
    def test_CNP(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            CNP.CNP_2(),
            CNP.CNP(), decimal=7)