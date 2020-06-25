import datetime
import sys
import locale

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


def is_int(s):
    try:
        if isinstance(s, str) or isinstance(s, int):
            int(s)
            return True
        else:
            return False
    except ValueError:
        return False


def is_num(s):
    try:
        locale.atoi(str(s))
    except ValueError:
        try:
            locale.atof(str(s))
        except ValueError:
            return False
    return True


def to_num(s):
    try:
        return locale.atoi(str(s))
    except ValueError:
        return locale.atof(str(s))


def to_str(value):
    try:
        strval = u''.join(value)
    except TypeError:
        strval = str(value, errors='ignore')
    return strval