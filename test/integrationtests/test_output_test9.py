# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from test_output import TestOutput


class test9_TestOutput(TestOutput):
    """
    Tests model generated output versus known
    static output.
    """
    __test__ = True

    def setUp(self):
        super(test9_TestOutput, self).setUp('test9.gms', 'test9_output.json')
