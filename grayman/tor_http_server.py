import pstats
from flask import Flask, request
from helpers import wrap_dict, unwrap_dict
import time
from rich import print
import uuid
import random

app = Flask(__name__)



@app.get("/tor")
def torget():

    ret = {
        "valid": True,
        "timestamp": int(time.time()),
        "shell_cmd": "echo got cmd from tor; date",
        "callback_freq": 1,
        "jobid" : str(uuid.uuid4())

    }

    return wrap_dict(ret)

@app.post("/tor")
def torpost():
    unwrapped = unwrap_dict(request.data)
    print(unwrapped)
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1337)
