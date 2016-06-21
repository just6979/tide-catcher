import calendar
import datetime
import json
import time
import urllib

import google_maps as maps


def get_api_key():
    return open("worldtides_api_key.txt").readline().strip()


def fetch(location, start_time, api_key):
    origin_lat, origin_lon = location

    request_url = "https://www.worldtides.info/api?{options}&lat={lat}&lon={lon}&start={start}&key={key}\n".format(
        options="extremes",
        lat=origin_lat,
        lon=origin_lon,
        start=start_time[0],
        key=api_key,
    )
    response = urllib.urlopen(request_url)

    return request_url, response.read()


def decode(data, tz_offset):
    data = json.loads(data)
    out = {}

    try:
        out['copyright'] = data['copyright']

        out['lat'] = data['responseLat']
        out['lon'] = data['responseLon']

        out['tides'] = []
        for tide in data['extremes']:
            epoch_time = datetime.datetime.utcfromtimestamp(tide['dt'])
            offset_delta = datetime.timedelta(hours=tz_offset)
            adjusted_timestamp = epoch_time + offset_delta
            out['tides'].append({
                'type': tide['type'],
                'date': adjusted_timestamp.date(),
                'time': adjusted_timestamp.time(),
            })
    except KeyError:
        out['error'] = "Error: Bad JSON Data\n"
        out['data'] = str(data)

    return out


def main():
    api_key = get_api_key()
    # Lynn, MA
    location = (42.478744, -71.001188)
    # right now in UTC as seconds since epoch
    start_time = calendar.timegm(time.gmtime()),
    url, response_data = fetch(location, start_time, api_key)
    print(url)
    offset = maps.get_tz_offset(location, start_time)
    out = decode(response_data, offset)
    print(out)


if __name__ == "__main__":
    main()
