def test_chunk():
    """tests the chunk function"""
    from helpers import chunk
    
    a = "deadbeef"
    b = [['de'], ['ad'], ['be'], ['ef']]
    assert chunk(a) == b

    a = [1,2,3,4,5,6]
    b = [[1,2],[3,4],[5,6]]
    assert chunk(a) == b
    a = [1,2,3,4,5,6]
    b = [[1,2,3],[4,5,6]]
    assert chunk(a, chunksize=3) == b
    a = [1,2,3,4,5,6]
    b = [1,2,3,4,5,6]
    assert chunk(a, chunksize=1) == b
    a = [1,2,3,4,5,6]
    b = [1,2,3,4,5,6]
    assert chunk(a, chunksize=1) == b