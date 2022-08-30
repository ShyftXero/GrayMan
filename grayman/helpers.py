import json
import vendor.aes as aes
import random
import time
import os
import base64
import binascii


if os.environ.get("GRAYMAN_VERBOSE") or os.environ.get("GRAYMAN_DEBUG"):
    from rich import print

    print("[red]DEBUGGING/VERBOSE[/red]")


def verbose(msg: object, *args, **kwargs):
    if os.environ.get("GRAYMAN_VERBOSE"):
        print(msg, *args, **kwargs)



def debug(msg: object, *args, **kwargs):
    if os.environ.get("GRAYMAN_DEBUG"):
        print(msg, *args, **kwargs)

def fake_ipv6(data:str):
    # print(f' faking {data} as IPv6 fields')
    hex_data = binascii.hexlify(data).decode()
    ret = list()
    chunks = chunk(hex_data,chunksize=32)

    for ipv6_chunk in chunks:
        addy = ':'.join([c for c in chunk(ipv6_chunk, chunksize=4)])
        ret.append(addy)
    ret = str(ret).replace('[','').replace(']','')
    # print(ret)
    return ret

def unfake_ipv6(addys:str) -> bytes:
    '''This accepts what looks like a Python list of ipv6 addresses and returns a byte sequence'''
    data = addys.replace('[','').replace(']','').replace("'",'').replace('"','').replace('','').replace(':','').replace(' ','').replace(',','')

    return binascii.unhexlify(data)

def chunk(iterable, chunksize: int = 2) -> list:
    """split item into chunksize-sized items
    returns a list
    """
    if chunksize < 2:
        return iterable

    ret = list()
    for i in range(0, len(iterable), chunksize):
        ret.append(iterable[i : i + chunksize])
    return ret


def _jitter(jitter_amount=0) -> int:
    if jitter_amount == 0:
        return 0
    return random.randint(jitter_amount * -1, jitter_amount)


def delay(base_time, jitter_amount: int = 0):
    if jitter_amount != 0:
        jitter_amount = _jitter(jitter_amount=jitter_amount)

    time.sleep(abs(base_time + jitter_amount))


# rewrap the aes lib
def _encrypt(
    data: bytes, key: bytes = b"1337deadbeef0000", iv: bytes = b"1337133713371337"
) -> bytes:
    return aes.AES(key).encrypt_ctr(data, iv)


def _decrypt(
    data: bytes, key: bytes = b"1337deadbeef0000", iv: bytes = b"1337133713371337"
) -> bytes:
    return aes.AES(key).decrypt_ctr(data, iv)


def unwrap_dict(
    package, keyprefix: bytes = b"1337deadbeef00", iv: bytes = b"1337133713371337"
) -> object:
    for i in range(256):
        try:
            key = f"{keyprefix.decode()}{i:02x}".encode()
            ct_json = base64.b64decode(package)
            raw = _decrypt(ct_json, key=key, iv=iv)
            obj = json.loads(raw)
            verbose(f"successfully unwrapped with key {key} and iv {iv}")
            return obj
        except json.JSONDecodeError as e:
            # print(e)
            pass
        except AssertionError as e:  # good key (for some reason) but failed the hmac validation from aes.decrypt
            # print(e)
            pass
        except UnicodeDecodeError as e:  #
            pass
            # return None

    debug("Unknown error")
    return None


def wrap_dict(
    package: dict, keyprefix: bytes = b"1337deadbeef00", iv: bytes = b"1337133713371337"
) -> str:
    rand_num = random.randint(0, 255)
    key = f"{keyprefix.decode()}{rand_num:02x}".encode()
    verbose(f"wrapping with key: {key} and iv {iv}")

    package['timestamp'] = int(time.time())

    pt_json = json.dumps(package).encode()
    ct_json = _encrypt(pt_json, key=key, iv=iv)
    b64_and_encrypted_json = base64.b64encode(ct_json)
    return b64_and_encrypted_json


# def agent_is_target(
#     target_ids: List[str] = [],
#     target_platforms: List[str] = [],
#     target_tags: List[str] = [],
# ):
#     if target_ids == [] and target_platforms == [] and target_tags == []: # got all defaults therefore it wasn't a targeted op.
#         return True

#     if target_ids == ["all"] :  # this is a targeted op targeting 'all'; for backwards compatibility ; will deprecate
#         print("this is a deprecated target mode... just omit and all agents will be targeted ")
#         return True

#     if AGENT_UUID  in target_ids:
#         print(f"I am a valid target uuid {AGENT_UUID}")
#         return True
#     elif AGENT_PLATFORM in target_platforms:
#         print(f"I am a valid target platform: {AGENT_PLATFORM}")
#         return True

#     for tag in AGENT_TAGS:
#         if tag in target_tags:
#             print(f"I have a target tag {tag}")
#             return True

#     return False
