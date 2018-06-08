import zmq
import random
import sys
import time
import json
from gwlfe import gwlfe, Parser
import cStringIO
import uuid
from gwlfe.Memoization import runid

def main():
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)

    while True:
        global runid
        gms = cStringIO.StringIO()
        temp = socket.recv()
        runid = uuid.uuid4()
        gms.write(temp)
        gms.seek(0)
        z = Parser.GmsReader(gms).read()
        start = time.time()
        print("Running Model")
        print(runid)
        result = gwlfe.run(z)
        socket.send_string(json.dumps(result, indent=4))
        print(time.time() - start)
        # time.sleep(1)

if __name__ == "__main__":
    main()