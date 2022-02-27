# these are here to signal requirement to pipreqs
# import gunicorn
# import flask
# import requests
# import rich


def test_requirements():
    assert __import__("gunicorn")
    assert __import__("flask")
    assert __import__("requests")
    assert __import__("rich")


def test_chunk():
    """tests the chunk function"""
    from helpers import chunk

    a = "deadbeef"
    b = ["de", "ad", "be", "ef"]
    assert chunk(a) == b

    a = [1, 2, 3, 4, 5, 6]
    b = [[1, 2], [3, 4], [5, 6]]
    assert chunk(a) == b
    a = [1, 2, 3, 4, 5, 6]
    b = [[1, 2, 3], [4, 5, 6]]
    assert chunk(a, chunksize=3) == b
    a = [1, 2, 3, 4, 5, 6]
    b = [1, 2, 3, 4, 5, 6]
    assert chunk(a, chunksize=1) == b
    a = [1, 2, 3, 4, 5, 6]
    b = [1, 2, 3, 4, 5, 6]
    assert chunk(a, chunksize=1) == b


def test_encryption():
    from helpers import _encrypt, _decrypt, unwrap_dict, wrap
    import json

    print("default key")
    pt = b"this is a message"
    ct = _encrypt(pt)
    recovered = _decrypt(ct)
    assert pt == recovered

    print("custom key")
    pt = b"this is a message"
    ct = _encrypt(pt, key="1337deadbeef00ff")
    recovered = _decrypt(ct, key="1337deadbeef00ff")
    assert pt == recovered

    print("json test")
    pt_json = """{"valid": true}"""
    json_obj = json.loads(pt_json)
    ct = _encrypt(pt_json)
    recovered = unwrap_dict(ct)
    print(json_obj, recovered)
    assert json_obj == recovered

    print("wrap unwrap test")
    pt_json = """{"valid": true}"""
    json_obj = json.loads(pt_json)
    ct = wrap(json_obj)
    recovered = unwrap_dict(ct)
    print(json_obj, recovered)
    assert json_obj == recovered


if __name__ == "__main__":
    test_encryption()
    test_chunk()
    test_requirements()
