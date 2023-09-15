from ..primitive import Boolean, Double, Integer


def test_integer_isvalid():
    for t in ("", "1.0", "1 000"):
        assert not Integer.isvalid(t)


def test_integer_from_string():
    for v in (-1, 0, 1, -100, 100):
        assert Integer.from_string(str(v)).value == v


def test_double_isvalid():
    for t in ("", "0,0", "1 000"):
        assert not Double.isvalid(t)


def test_double_from_string():
    for v in (-1, 0, 1, -1.1, -100, 100):
        assert Double.from_string(str(v)).value == v


def test_boolean_isvalid():
    for t in ("FALSE", "True"):
        assert Boolean.isvalid(t) is False


def test_boolean_from_string():
    assert Boolean.from_string("true").value is True
    assert Boolean.from_string("false").value is False
