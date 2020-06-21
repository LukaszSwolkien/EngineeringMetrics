import datetime
import sys


def die(message):
    print(message)
    sys.exit(1)


def to_ts(dt):
    td = dt - datetime.datetime(1970, 1, 1)
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6


def to_dt(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def utc_ts(dt=datetime.datetime.utcnow()):
    """ timestamp in seconds """
    return to_ts(dt)


def day_ts(dt=datetime.datetime.utcnow()):
    """ timestamp in seconds for a day """
    return to_ts(datetime.datetime(year=dt.year, month=dt.month, day=dt.day))
