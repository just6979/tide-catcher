import json
import time
import urllib2

base_url = """\
https://maps.googleapis.com/maps/api/timezone/json?\
location={location}&timestamp={timestamp}&key={api_key}\
"""


def get_api_key():
    return open("google_api_key.txt").readline().strip()


def fetch_data(location, timestamp):
    # TODO: handle errors
    api_key = get_api_key()
    location_string = "%s,%s" % location

    request_url = base_url.format(
        location=location_string,
        timestamp=timestamp[0],
        api_key=api_key,
    )
    response = urllib2.urlopen(request_url)

    return request_url, response.read()


def decode_json(data):
    out = {}
    error = False

    data = json.loads(data)

    try:
        offset = data['rawOffset']
        if 'dstOffset' in data:
            offset = offset + data['dstOffset']
        out['offset'] = offset / 3600
        out['name'] = data['timeZoneName']
    except KeyError:
        error = {
            'msg': "Error: Bad JSON Data\n",
            'data': str(data),
        }

    return out, error


def get_tz_offset(location, timestamp):
    request_url, json_data = fetch_data(location, timestamp)
    data, err = decode_json(json_data)
    if not err:
        return request_url, data['offset'], data['name']


def main():
    # Lynn, MA
    location = (42.478744, -71.001188)
    # right now in UTC as seconds since epoch
    timestamp = time.time(),
    request_url, json_data = fetch_data(location, timestamp)
    print(request_url)
    data, err = decode_json(json_data)
    if not err:
        print('Offset = %d hours' % data['offset'])
    else:
        print data['error']
        print data['data']


if __name__ == "__main__":
    main()
