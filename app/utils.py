import datetime

DATE_FORMAT = "%m-%d"
# TIME_FORMAT = "%H:%M"
TIME_FORMAT = "%I:%M %p"
DAY_FORMAT = "%a"


def offset_timestamp(timestamp, tz_offset):
    return timestamp + datetime.timedelta(hours=tz_offset)


def to_nearest_minute(timestamp):
    if timestamp.second < 30:
        return timestamp.replace(second=0)
    else:
        return timestamp.replace(minute=timestamp.minute + 1, second=0)


# TODO: ?convert error dicts to exceptions?
def error_builder(mod_name, status, error='', msg=''):
    return {
        'module': mod_name,
        'status': status,
        'error': error,
        'msg': msg
    }
