from dataclass import dataclass
from abc import abc
import requests

@dataclass
class Beacon(abc):
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
class Transport(abc):
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
    endpoint:str
    server:str

    def send(self, payload:bytes):
        print(f'sending {payload} via http transport on {self.server}{self.endpoint}')
        
    
    def recv(self, payload:bytes):
        print(f'sending {payload} via http transport on {self.server}{self.endpoint}')
        

@dataclass
class DNSTransport(Transport):
    """Class for dns based c2 channel"""
    domain:str

    def send(self, payload:bytes):
        print(f'sending {payload} via DNS on {self.domain}')
    
    def recv(self, payload:bytes):
        print(f'getting {payload} via DNS on {self.domain}')







