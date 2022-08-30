from flask import Flask, request, make_response
from helpers import wrap_dict, unwrap_dict, fake_ipv6, unfake_ipv6
import time
from rich import print
import uuid
import random

app = Flask(__name__)



@app.get("/longhaul")
def longhaul():

    ret = {
        "valid": True,
        "timestamp": int(time.time()),
        "shell_cmd": "echo got cmd from longhaul; date",
        "callback_freq": 1,
        "jobid" : str(uuid.uuid4())

    }

    return wrap_dict(ret)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
