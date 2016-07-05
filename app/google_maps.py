import calendar
import datetime
import json
import pprint
import urllib2

base_url = """\
https://maps.googleapis.com/maps/api/timezone/json?\
location={location}&timestamp={timestamp}&key={api_key}\
"""


def get_api_key():
    return open("google_api_key.txt").readline().strip()


def fetch(api_key, location, timestamp):
    # TODO: handle errors
    location_string = "%s,%s" % location

    request_url = base_url.format(
        location=location_string,
        # convert datetime to unix time
        timestamp=calendar.timegm(timestamp.timetuple()),
        api_key=api_key,
    )
    response = urllib2.urlopen(request_url)

    return request_url, response.read()


def decode(data):
    out = {}

    data = json.loads(data)

    try:
        offset = data['rawOffset']
        if 'dstOffset' in data:
            offset = offset + data['dstOffset']
        out['offset'] = offset / 3600
        out['name'] = data['timeZoneName']
    except KeyError:
        out['error'] = "Error: Bad JSON Data\n"
        out['data'] = str(data)

    return out


def fetch_and_decode(api_key, location, timestamp):
    tz_url, tz_response = fetch(api_key, location, timestamp)
    tz = decode(tz_response)

    return tz, tz_url


def main():
    # Lynn, MA
    request_lat = 42.478744
    request_lon = -71.001188
    request_location = (request_lat, request_lon)

    # right now in UTC as seconds since epoch
    timestamp = datetime.datetime.utcnow()

    tz_url, tz_response = fetch(get_api_key(), request_location, timestamp)
    tz = decode(tz_response)

    pp = pprint.PrettyPrinter()

    print(tz_url)
    if 'error' in tz:
        print(tz['error'])
        pp.pprint(tz['data'])
    else:
        print('Offset = %s hours' % tz['offset'])


if __name__ == "__main__":
    main()
