import calendar
import datetime
import json
import urllib2
from pprint import pprint

import utils

from . import config

_module = 'Google Maps Timezone API'

_base_url = """\
https://maps.googleapis.com/maps/api/timezone/json?\
location={location}&timestamp={timestamp}&key={api_key}\
"""


def get_tz_offset(location, timestamp):
    tz_data = {}

    location_string = '%s,%s' % location

    # convert datetime to unix time
    unix_timestamp = calendar.timegm(timestamp.timetuple())
    request_url = _base_url.format(
        location=location_string,
        timestamp=unix_timestamp,
        api_key=config.google_maps_api_key,
    )

    response = urllib2.urlopen(request_url).read()
    response_data = json.loads(response)

    try:
        status = response_data['status']
        if status == 'OK':
            tz_data['status'] = status
            offset = response_data['rawOffset']
            if 'dstOffset' in response_data:
                offset = offset + response_data['dstOffset']
            tz_data['offset'] = offset / 3600
            tz_data['name'] = response_data['timeZoneName']
        else:
            tz_data = utils.error_builder(
                module=_module,
                status=status,
                msg=response_data.get('errorMessage')
            )
    except KeyError:
        tz_data = utils.error_builder(
            module=_module,
            status='JSON_DECODING_ERROR',
            msg=str(response_data)
        )

    return tz_data


def _main():
    request_location = utils.test_location
    # right now in UTC as seconds since epoch
    timestamp = datetime.datetime.utcnow()

    print('Testing Google Maps Timezone API:')
    tz_data = get_tz_offset(request_location, timestamp)
    print('Request completed.')
    if tz_data['status'] == 'OK':
        print('SUCCESS: Accepted API Key and returned results:')
        pprint(tz_data)
    else:
        print('FAILURE:')
        print(utils.error_dump(tz_data))

    # now we break it on purpose
    print('')
    global _api_key
    _api_key = 'foobar'
    print('Testing Google Maps Timezone API error handling (bad API key):')
    tz_data = get_tz_offset(request_location, timestamp)
    print('Request completed')
    if tz_data['status'] == 'OK':
        print('FAILURE: Accepted bogus API Key:')
        pprint(tz_data)
    else:
        print('SUCCESS: Failed on bogus API Key:')
        print(utils.error_dump(tz_data))


if __name__ == '__main__':
    _main()
