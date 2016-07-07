import datetime

DATE_FORMAT = "%m-%d"
# DATE_FORMAT = "%m-%d
DAY_FORMAT = "%a"
TIME_FORMAT = "%H:%M"


def offset_timestamp(timestamp, tz_offset):
    offset_delta = datetime.timedelta(hours=tz_offset)
    adjusted_timestamp = timestamp + offset_delta
    return adjusted_timestamp
