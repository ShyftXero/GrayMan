import re
import requests
import time
from helpers import wrap, unwrap, delay
from classes import HTTPTransport
import random

DWELL_TIME = 10
URL = "https://shyft.us"
PROXIES = list()




def operate():
	t1 = HTTPTransport(server="http://localhost/ep1", proxies=PROXIES)
	t2 = HTTPTransport(server="http://localhost/ep2", proxies=PROXIES)
	t3 = HTTPTransport(server="http://localhost/ep3", proxies=PROXIES)
	transports = [t1,t2,t3]
	while True:
	
		try:
			transport = random.choice(transports) 
			resp = transport.recv()
			print(resp.text)
		except requests.exceptions.ConnectionError as e:
			print(e)
		except BaseException as e:
			print(e)
		







		jitter = DWELL_TIME // 4 
		delay(DWELL_TIME, jitter_amount=jitter) 

if __name__ == '__main__':
	try:
		operate()
	except KeyboardInterrupt as e:
		print('shutting down', e)