import datetime

DATE_FORMAT = '%m-%d'
# TIME_FORMAT = '%H:%M'
TIME_FORMAT = '%I:%M %p'
DAY_FORMAT = '%a'


def offset_timestamp(timestamp, tz_offset):
    return timestamp + datetime.timedelta(hours=tz_offset)


def to_nearest_minute(timestamp):
    if timestamp.second < 30:
        return timestamp.replace(second=0)
    else:  # second >= 30
        return timestamp.replace(second=0) + datetime.timedelta(minutes=1)


# TODO: ?convert error dicts to exceptions?
def error_builder(mod_name, status, error='', msg=''):
    return {
        'module': mod_name,
        'status': status,
        'error': error,
        'msg': msg
    }
