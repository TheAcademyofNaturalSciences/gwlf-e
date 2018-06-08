#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
import json
import logging
import time

# from gwlfe.gwlfe import run
# from gwlfe.Parser import GmsReader
from gwlfe.combined import run
from gwlfe.combined import GmsReader


def main():
    log = logging.getLogger('gwlfe')
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    log.addHandler(ch)

    gms_filename = sys.argv[1]

    fp = open(gms_filename, 'r')
    z = GmsReader(fp).read()
    start = time.time()
    result = run(z)
    print(time.time()-start)
    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
