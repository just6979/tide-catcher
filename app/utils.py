import datetime

DATE_FORMAT = "%m-%d-%Y"
# DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


def adjusted_datetime(timestamp, tz_offset):
    offset_delta = datetime.timedelta(hours=tz_offset)
    adjusted_timestamp = timestamp + offset_delta
    return adjusted_timestamp
