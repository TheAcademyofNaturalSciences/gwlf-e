#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
import time

import zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)


def main():
    log = logging.getLogger('gwlfe')
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    log.addHandler(ch)

    for gms_filename in sys.argv[1:]:
        start = time.time()
        fp = open(gms_filename, 'r')
        socket.send_string(fp.read())
        result = socket.recv()
        print(result)
        print(time.time() - start)


if __name__ == '__main__':
    main()
