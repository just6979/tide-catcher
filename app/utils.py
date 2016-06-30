import datetime


def adjusted_datetime(timestamp, tz_offset):
    epoch_time = datetime.datetime.utcfromtimestamp(timestamp)
    offset_delta = datetime.timedelta(hours=tz_offset)
    adjusted_timestamp = epoch_time + offset_delta
    return adjusted_timestamp
