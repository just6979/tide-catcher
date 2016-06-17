import calendar
import json
import time
import urllib


def get_api_key():
    return open("worldtides_api_key.txt").readline().strip()


def fetch(api_key):
    # Lynn, MA
    origin_lat = 42.478744
    origin_lon = -71.001188
    origin_location = (origin_lat, origin_lon)

    request_url = "https://www.worldtides.info/api?{options}&lat={lat}&lon={lon}&start={start}&key={key}\n".format(
        options="extremes",
        lat=origin_lat,
        lon=origin_lon,
        # right now in UTC as seconds since epoch
        start=calendar.timegm(time.gmtime()),
        key=api_key
    )
    response = urllib.urlopen(request_url)

    return request_url, response.read()


def decode(data):
    data = json.loads(data)
    out = {}

    try:
        out['copyright'] = data['copyright']

        result_lat = data['responseLat']
        result_lon = data['responseLon']

        out['location'] = "%s, %s" % (result_lat, result_lon)

        out['tides'] = []
        for tide in data['extremes']:
            out['tides'].append("{type:>4}  {time}\n".format(
                type=tide['type'],
                time=time.asctime(time.localtime(tide['dt']))
            ))
    except KeyError:
        out['error'] = "Error: Bad JSON Data\n"
        out['data'] = str(data)

    return out


if __name__ == "__main__":
    key = get_api_key()
    url, response_data = fetch(key)
    print(url)
    out = decode(response_data)
    print(out)
