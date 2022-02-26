from dataclasses import dataclass
from abc import ABC
import requests

@dataclass
class Beacon(ABC):
    def beacon(self, payload):
        ...

class HTTPBeacon(Beacon):
    server:str
    endpoint:str
    def beacon(self, payload:bytes):
        print(f"beaconing via dns to {self.server}{self.endpoint}")

        
class DNSBeacon(Beacon):
    server:str
    def beacon(self, payload:bytes):
        print(f"beaconing via dns to {self.server}")


@dataclass
class Transport(ABC):
    """C2 transport base class"""
    def send(self, payload:bytes):
        ...
    def recv(self, payload:bytes):
        ...

@dataclass
class HTTPTransport(Transport):
    """Class for http/s based c2 channel
    Meant for burnable short-haul comms or bandwidth-heavy activity
    """
    
    server:str
    proxies:tuple = tuple()
    endpoint:str = '/'
    send_method:str = 'post'
    recv_method:str = 'get'
    good_status_code = "200"
    user_agent:str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, payload:bytes, **kwargs):
        print(f'sending {payload} via http transport on {self.server}{self.endpoint}')
        headers = {
		    'User-Agent':self.user_agent
        }

        return requests.post(self.server, headers=headers, proxies=kwargs.get('proxies',[]))
        
    
    def recv(self):
        print(f'getting  via http transport on {self.server}{self.endpoint}')
        headers = {
		    'User-Agent':self.user_agent
        }

        return requests.get(self.server, headers=headers)
        

@dataclass
class DNSTransport(Transport):
    """Class for dns based c2 channel"""
    domain:str

    def send(self, payload:bytes):
        print(f'sending {payload} via DNS on {self.domain}')
    
    def recv(self, payload:bytes):
        print(f'getting {payload} via DNS on {self.domain}')







