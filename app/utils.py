import datetime

DATE_FORMAT = "%m-%d"
DAY_FORMAT = "%a"
TIME_FORMAT = "%H:%M"


def offset_timestamp(timestamp, tz_offset):
    offset_delta = datetime.timedelta(hours=tz_offset)
    adjusted_timestamp = timestamp + offset_delta
    return adjusted_timestamp


def to_nearest_minute(timestamp):
    if timestamp.second < 30:
        return timestamp.replace(second=0)
    else:
        return timestamp.replace(minute=timestamp.minute + 1, second=0)
