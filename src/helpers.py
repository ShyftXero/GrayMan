from lib2to3.pytree import Base
# from typing import Iterable
import json
import vendor.aes as aes
import random
import time
import uuid

def chunk(iterable, chunksize:int=2) -> list:
    """split item into chunksize-sized items
    returns a list
    """
    if chunksize < 2:
        return iterable

    ret = list()
    for i in range(0, len(iterable), chunksize):
        ret.append(iterable[i:i+chunksize])
    return ret

def _jitter(jitter_amount=0) -> int:
    if jitter_amount == 0:
        return 0
    return random.randint(jitter_amount * -1, jitter_amount)


def delay(base_time, jitter_amount):
    if jitter_amount != 0:
        jitter_amount = _jitter(jitter_amount=jitter_amount)

    time.sleep(abs(base_time + jitter_amount))

# rewrap the aes lib
def _encrypt(data:bytes, key:bytes=b"1337deadbeef0000") -> bytes:
    return aes.encrypt(key, data)

def _decrypt(data:bytes, key:bytes=b"1337deadbeef0000") -> bytes:
    return aes.decrypt(key, data)

def unwrap(data, keyprefix:bytes=b'1337deadbeef00') -> object:
    for i in range(256):
        try:
            key = f'{keyprefix.decode()}{i:02x}'.encode()
            print(key)
            obj =  json.loads(_decrypt(data, key=key))
            return obj
        except json.JSONDecodeError as e:
            print(e)
            # pass
        except AssertionError as e: # failed the hmac validation from aes.decrypt
            # print(e)
            pass
        except BaseException as e:
            print(e)
        
def wrap(obj:object, keyprefix:bytes=b'1337deadbeef00') -> bytes:
    rand_num = random.randint(0,255)
    key = f'{keyprefix.decode()}{rand_num:02x}'.encode()
    print(f'wrapping with key: {key}')
    return _encrypt(json.dumps(obj), key=key)



