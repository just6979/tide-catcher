import datetime

DATE_FORMAT = '%m-%d'
# TIME_FORMAT = '%H:%M'
TIME_FORMAT = '%I:%M %p'
DAY_FORMAT = '%a'

# Lynn, MA
test_latitude = 42.478744
test_longitude = -71.001188
test_location = (test_latitude, test_longitude)


def offset_timestamp(timestamp, tz_offset):
    return timestamp + datetime.timedelta(hours=tz_offset)


def to_nearest_minute(timestamp):
    if timestamp.second < 30:
        return timestamp.replace(second=0)
    else:  # second >= 30
        return timestamp.replace(second=0) + datetime.timedelta(minutes=1)


# TODO: ?convert error dicts to exceptions?
def error_builder(module, status, msg=u''):
    return {
        'module': module,
        'status': status,
        'msg': msg
    }


def error_dump(error):
    out = \
        'Module: {module}\n' \
        'Status: {status}\n' \
        'Message: {msg}\n'

    return out.format(
        module=error['module'],
        status=error['status'],
        msg=error['msg']
    )
