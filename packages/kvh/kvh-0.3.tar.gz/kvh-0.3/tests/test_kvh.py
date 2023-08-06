from pathlib import Path
import pytest
import kvh.kvh as kv

def test_0():
    fn=str(Path(__file__).parent/"test0.kvh")
    # we use strip_white for Windows where "\r" is kept otherwise.
    assert kv.kvh_read(fn, strip_white=True) == [("key", "value")]
    assert kv.kvh_read(open(fn, "rb"), strip_white=True) == [("key", "value")]

def test_err():
    with pytest.raises(RuntimeError):
        kv.kvh_read("non existing file")
    with pytest.raises(TypeError):
        kv.kvh_read(["no way to read a list"])
