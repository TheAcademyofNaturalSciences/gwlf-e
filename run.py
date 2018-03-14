#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
import json
import logging

from gwlfe import gwlfe, parser


def main():
    log = logging.getLogger('gwlfe')
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    log.addHandler(ch)

    gms_filename = sys.argv[1]

    fp = open(gms_filename, 'r')
    z = parser.GmsReader(fp).read()
    result,z = gwlfe.run(z)
    z.unique_variable_file_usages()
    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
