import ia.common.helpers as h


def test_to_str():
    s = h.to_str("Ō∑ę®†ī¨^óĻąś∂ń©ķ∆Żłźć√ļńĶ≤≥÷")
    assert s == "Ō∑ę®†ī¨^óĻąś∂ń©ķ∆Żłźć√ļńĶ≤≥÷"


def test_to_num():
    n = h.to_num("10")
    assert n == 10
    n = h.to_num("0.1")
    assert n == 0.1


def test_is_num():
    assert h.is_num(10)
    assert h.is_num(-5.14)
    assert h.is_num("10.1")
    assert h.is_num("-4.12")
    assert h.is_num("1.23E-7")
    assert not h.is_num("asd")

def test_is_int():
    assert h.is_int(10)
    assert not h.is_int(-5.14)
    assert h.is_int("101")
    assert not h.is_int("10.1")
    assert not h.is_int("-4.12")
    assert h.is_int("1e1")
    assert not h.is_int("asd")

