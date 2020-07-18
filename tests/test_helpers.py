import datetime

import ia.common.helpers as h


def test_to_str():
    s = h.to_str("Ō∑ę®†ī¨^óĻąś∂ń©ķ∆Żłźć√ļńĶ≤≥÷😀♞ü")
    assert s == "Ō∑ę®†ī¨^óĻąś∂ń©ķ∆Żłźć√ļńĶ≤≥÷😀♞ü"


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


def test_to_ts():
    first_jan_2020 = datetime.datetime(year=2020, month=1, day=1)
    ts = h.to_ts(first_jan_2020)
    assert ts == 1577833200


def test_to_dt():
    first_jan_2020 = datetime.datetime(year=2020, month=1, day=1)
    first_jan_2020_ts = h.to_ts(first_jan_2020)
    dt = h.to_dt(first_jan_2020_ts)
    assert dt == first_jan_2020


def test_utc_ts():
    d = datetime.datetime.utcnow()
    utc_ts = h.utc_ts(d)
    assert h.to_ts(d) == utc_ts


def test_day_ts():
    dt = datetime.datetime.utcnow()
    day = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
    day_ts = h.day_ts(day)
    assert h.to_ts(day) == day_ts

def test_business_days():
    date_a = datetime.datetime(year=2020, month=7, day=16)
    date_b = datetime.datetime(year=2020, month=7, day=20)

    d = h.business_days(date_a, date_b)
    assert d.days == 2

    date_a = datetime.datetime(year=2020, month=7, day=17)
    date_b = datetime.datetime(year=2020, month=7, day=17)

    d = h.business_days(date_a, date_b)
    assert d.days == 0
