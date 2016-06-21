import calendar
import datetime
import json
import time
import urllib


def get_api_key():
    return open("worldtides_api_key.txt").readline().strip()


def fetch(location, start_time, api_key):
    origin_lat, origin_lon = location

    request_url = "https://www.worldtides.info/api?{options}&lat={lat}&lon={lon}&start={start}&key={key}\n".format(
        options="extremes",
        lat=origin_lat,
        lon=origin_lon,
        start=start_time,
        key=api_key,
    )
    response = urllib.urlopen(request_url)

    return request_url, response.read()


def decode(data):
    data = json.loads(data)
    out = {}

    try:
        out['copyright'] = data['copyright']

        out['lat'] = data['responseLat']
        out['lon'] = data['responseLon']

        out['tides'] = []
        for tide in data['extremes']:
            epoch_time = datetime.datetime.utcfromtimestamp(tide['dt'])

            out['tides'].append({
                'type': tide['type'],
                'date': epoch_time.date(),
                'time': epoch_time.time(),
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
    out = decode(response_data)
    print(out)


if __name__ == "__main__":
    main()
