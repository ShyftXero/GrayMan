from typing import Iterable
def chunk(item:Iterable, chunksize:int=2) -> list:
    """split item into chunksize-sized items
    returns a list
    """
    if chunksize < 2:
        return item

    ret = list()
    for i in range(0, len(item), chunksize):
        ret.append(item[i:i+chunksize])
    return ret


