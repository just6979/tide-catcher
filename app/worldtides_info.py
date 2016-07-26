import calendar
import json
import logging
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
    logging.info(request_url)
    response = urllib.urlopen(request_url)

    return request_url, response.read()


def decode(data, utc_now_stamp, tz_offset):
    out = {}

    try:
        data = json.loads(data)
    except ValueError as e:
        # we got bad JSON from worldtides.info, probably a 500 ISE
        # TODO: instead of an error, return a warning that the source is down &
        # force a cache read instead
        out['status'] = 500
        out['error'] = e.message
        out['msg'] = \
            'Our tides information source seems to be down at the moment, ' \
            'please try again later.'
    else:
        # looks like we got a JSON response, try to extract data from it
        try:
            status = data['status']
            if status == 200:
                out['status'] = 'OK'
                out['copyright'] = data['copyright']
                out['lat'] = data['responseLat']
                out['lon'] = data['responseLon']
                out['station'] = data['station']
                out['tides'] = []

                for tide in data['extremes']:
                    utc_timestamp = datetime.datetime.utcfromtimestamp(tide['dt'])
                    timestamp = to_nearest_minute(
                        offset_timestamp(utc_timestamp, tz_offset))
                    now_stamp = to_nearest_minute(
                        offset_timestamp(utc_now_stamp, tz_offset))

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
            else:
                out['status'] = status
                out['error'] = data['error']
                out['msg'] = ''
        except KeyError:
            out['status'] = 500
            out['error'] = "Error: Bad JSON Data\n"
            out['data'] = str(data)

    return out


def fetch_and_decode(tides_api_key, location, start_time,
                     now_time, tz_offset):
    # TODO: adjust timezone based on request location or response location?
    tides_url, tides_response = fetch(tides_api_key, location, start_time)
    tides = decode(tides_response, now_time, tz_offset)

    return tides, tides_url


def fetch_stations(api_key):
    stations_url = "https://www.worldtides.info/api?stations&key={key}".format(
        options="stations",
        key=api_key,
    )
    response = urllib.urlopen(stations_url)
    data = json.loads(response.read())

    try:
        out = data['stations']
    except KeyError:
        out = {
            'error': "Error: Bad JSON Data\n",
            'data': str(data)
        }

    return stations_url, out


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
