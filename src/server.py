from flask import Flask, request
import json
from helpers import wrap, unwrap

app = Flask(__name__)

@app.get("/")
def index():
	return "index"

@app.get("/ep<int:num>")
def endpoint(num):

	cmds = {
		1: 'id', 
		2: 'date', 
		3: 'uname -a',
		4: "curl ifconfig.me",
	}
	ret = {
		f'ep': num,
		'cmd': cmds.get(num, 'hostname')
	}
	return ret





if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)