from flask import Flask, request
import json
from helpers import wrap_dict, unwrap_dict
import time

app = Flask(__name__)


@app.get("/")
def index():
    return "index"


@app.get("/ep<int:num>")
def endpoint(num):
    # if request is missing a type of header e.g. X-Forwarded-For
    # return dummy page
    # otherwise do this stuff

    cmds = {
        1: "id",
        2: "date",
        3: "uname -a",
        4: "curl ifconfig.me",
    }
    ret = {
        "valid": True,
        "timestamp": int(time.time()),
        "ep": num,
        "cmd": cmds.get(num, "hostname"),
        "dwell_time": 10,
    }
    return wrap_dict(ret)


@app.post("/ep<int:num>")
def catch(num):
    print("got post", request.data)
    print(unwrap_dict(request.data))
    return "asdf", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
