import unittest
from unittest import skip
from mock import patch
import numpy as np
from gwlfe import Parser
from gwlfe import QTotal


class TestQTotal(unittest.TestCase):
    def setUp(self):
        input_file = open('unittests/input_4.gms', 'r')
        self.z = Parser.GmsReader(input_file).read()

    def test_QTotal_ground_truth(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            np.load("unittests/QTotal.npy"),
            QTotal.QTotal(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0,
                          z.AntMoist_0,
                          z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN), decimal=7)

    # @skip("not ready")
    def test_QTotal(self):
        z = self.z
        np.testing.assert_array_almost_equal(
            QTotal.QTotal(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0, z.AntMoist_0,
                            z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN),
            QTotal.QTotal_2(z.NYrs, z.DaysMonth, z.Temp, z.InitSnow_0, z.Prec, z.NRur, z.NUrb, z.Area, z.CNI_0, z.AntMoist_0,
                            z.Grow_0, z.CNP_0, z.Imper, z.ISRR, z.ISRA, z.CN), decimal=7)