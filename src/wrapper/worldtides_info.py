import calendar
import json
import logging
import os
import urllib.request as request
from datetime import datetime, timedelta, timezone
from pprint import pprint

from . import google_maps
from .. import utils

_module = 'World Tides API'

_base_url = '''\
https://www.worldtides.info/api?\
{options}&lat={lat}&lon={lon}&start={start}&key={key}\
'''

_api_key = os.environ['WORLDTIDES_INFO_API_KEY']


def fetch_tides(location, utc_start_time, utc_now_stamp, tz_offset):
    # TODO: adjust timezone based on request location or response location?
    origin_lat, origin_lon = location

    request_url = _base_url.format(
        options='extremes',
        lat=origin_lat,
        lon=origin_lon,
        start=calendar.timegm(utc_start_time.timetuple()),
        key=_api_key,
    )
    logging.info(request_url)
    response = request.urlopen(request_url)
    data = response.read()

    try:
        data = json.loads(data)
    except ValueError as e:
        # we got bad JSON from worldtides.info, probably a 500 ISE
        out = utils.error_builder(
            _module,
            500,
            'Our tides information source seems to be down at the moment, '
            'please try again later.' + e.message
        )
        return out

    # looks like we got a JSON response, try to extract data from it
    try:
        status = data['status']
        if status == 200:
            out = {
                'status': 'OK',
                'responseLat': data['responseLat'],
                'responseLon': data['responseLon'],
                'copyright': data['copyright'],
                'tides': []
            }

            for tide in data['extremes']:
                utc_timestamp = datetime.fromtimestamp(
                    tide['dt'], timezone.utc)
                timestamp = utils.to_nearest_minute(
                    utils.offset_timestamp(utc_timestamp, tz_offset))
                now_stamp = utils.to_nearest_minute(
                    utils.offset_timestamp(utc_now_stamp, tz_offset))

                if timestamp < now_stamp:
                    prior = 'prior'
                else:
                    prior = 'future'

                out['tides'].append({
                    'type': tide['type'],
                    'date': timestamp.strftime(utils.MM_DD_DATE_FORMAT),
                    'day': timestamp.strftime(utils.DAY_FORMAT),
                    # TODO: round times to nearest minute
                    'time': timestamp.strftime(utils.TIME_FORMAT),
                    'prior': prior,
                })
            return out
        else:
            return utils.error_builder(
                module=_module,
                status=status,
                msg=data['error']
            )
    except KeyError:
        return utils.error_builder(
            module=_module,
            status='JSON_DECODING_ERROR',
            msg=str(data)
        )


def fetch_stations():
    stations_url = 'https://www.worldtides.info/api?stations&key={key}'.format(
        options='stations',
        key=_api_key,
    )
    logging.info(stations_url)
    response = request.urlopen(stations_url)
    data = response.read()

    try:
        data = json.loads(data)
    except ValueError as e:
        # we got bad JSON from worldtides.info, probably a 500 ISE
        return utils.error_builder(
            module=_module,
            status=500,
            msg='Our tides information source seems to be down at the moment, '
                'please try again later.' + e.message
        )

    try:
        return {
            'status': 'OK',
            'stations': data['stations']
        }
    except KeyError:
        return utils.error_builder(
            module=_module,
            status='Error: Bad JSON Data\n',
            msg=str(data)
        )


def main():
    print('Test WorldTides API:')

    req_loc = utils.test_location
    # right now in  UTC as unix time
    utc_now = datetime.utcnow()
    # minus 12 hours to make sure we get the last tide
    utc_minus_12 = utc_now + timedelta(hours=-12)

    print('Getting timezone offset from Google Maps API:')
    tz_data = google_maps.get_tz_offset(req_loc, utc_now)
    if tz_data['status'] == 'OK':
        print('SUCCESS')
        pass
    else:
        print('FAILURE:')
        print(utils.error_dump(tz_data))
        return

    print('Testing WorldTides Location API:')
    tides_data = fetch_tides(req_loc, utc_minus_12, utc_now, tz_data['offset'])
    print('Request completed.')
    if tides_data['status'] == 'OK':
        print('SUCCESS: Accepted API Key and returned results:')
        print(tides_data)
    else:
        print('FAILURE:')
        print(utils.error_dump(tides_data))

    # now we break it on purpose
    print('')
    print('Testing WorldTides API error handling (bad API key):')
    global _api_key
    _api_key = 'foobar'

    tides_data = fetch_tides(req_loc, utc_minus_12, utc_now, tz_data['offset'])
    print('Request completed')
    if tides_data['status'] == 'OK':
        print('FAILURE: Accepted bogus API Key:')
        pprint(tides_data)
    else:
        print('SUCCESS: Failed on bogus API Key:')
        print(utils.error_dump(tides_data))


if __name__ == '__main__':
    main()
