import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import StreamBankEros


class TestStreamBankEros(unittest.TestCase):
    def setUp(self):
        input_file = open('input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()


    @skip('Not Ready Yet.')
    def test_StreamBankEros(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            StreamBankEros.StreamBankEros_2(),
            StreamBankEros.StreamBankEros(), decimal=7)