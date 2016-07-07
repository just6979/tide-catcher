import calendar
import json
import pprint
import urllib

import google_maps as maps_api
from utils import *

base_url = """\
https://www.worldtides.info/api?\
{options}&lat={lat}&lon={lon}&start={start}&key={key}\
"""


def get_api_key():
    return open("worldtides_api_key.txt").readline().strip()


def fetch(api_key, location, utc_start_time):
    # TODO: handle errors
    origin_lat, origin_lon = location

    request_url = base_url.format(
        options="extremes",
        lat=origin_lat,
        lon=origin_lon,
        start=calendar.timegm(utc_start_time.timetuple()),
        key=api_key,
    )
    response = urllib.urlopen(request_url)

    return request_url, response.read()


def decode(data, utc_now_stamp, tz_offset):
    out = {}

    data = json.loads(data)

    try:
        out['copyright'] = data['copyright']
        out['lat'] = data['responseLat']
        out['lon'] = data['responseLon']
        out['station'] = data['station']
        out['tides'] = []

        for tide in data['extremes']:
            utc_timestamp = datetime.datetime.utcfromtimestamp(tide['dt'])
            timestamp = offset_timestamp(utc_timestamp, tz_offset)
            timestamp = to_nearest_minute(timestamp)
            now_stamp = offset_timestamp(utc_now_stamp, tz_offset)

            if timestamp < now_stamp:
                prior = 'prior'
            else:
                prior = 'future'

            out['tides'].append({
                'type': tide['type'],
                'date': timestamp.strftime(DATE_FORMAT),
                'day': timestamp.strftime(DAY_FORMAT),
                # TODO: round times to nearest minute
                'time': timestamp.strftime(TIME_FORMAT),
                'prior': prior,
            })
    except KeyError:
        out['error'] = "Error: Bad JSON Data\n"
        out['data'] = str(data)

    return out


def fetch_and_decode(tides_api_key, maps_api_key, location, start_time, now_time):
    # TODO: adjust timezone based on request location or response location?
    tz_url, tz_response = maps_api.fetch(maps_api_key, location, start_time)
    tz = maps_api.decode(tz_response)

    tides_url, tides_response = fetch(tides_api_key, location, start_time)
    tides = decode(tides_response, now_time, tz['offset'])

    return (tides, tides_url), (tz, tz_url)


def main():
    tides_api_key = get_api_key()
    maps_api_key = maps_api.get_api_key()

    # Lynn, MA
    request_lat = 42.478744
    request_lon = -71.001188
    request_location = (request_lat, request_lon)

    # right now in  UTC as unix time
    utc_now = datetime.datetime.utcnow()
    # minus 12 hours to make sure we get the last tide
    utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

    (tides, tides_url), (tz, tz_url) = fetch_and_decode(
        tides_api_key, maps_api_key, request_location, utc_minus_12, utc_now
    )

    pp = pprint.PrettyPrinter()

    print(tides_url)
    if 'error' in tz:
        print(tz['error'])
        pp.pprint(tz['data'])
    elif 'error' in tides:
        print(tides['error'])
        pp.pprint(tides['data'])
    else:
        pp.pprint(tides)


if __name__ == "__main__":
    main()
