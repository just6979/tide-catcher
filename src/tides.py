import datetime
import os

from . import utils
from .datastore import Station
from .wrapper import google_maps, worldtides_info

_module = 'Tides'

maps_api_key = os.environ['GOOGLE_MAPS_API_KEY']
tides_api_key = os.environ['WORLDTIDES_INFO_API_KEY']


def for_location(location: list):

    # right now in UTC as naive datetime
    utc_now = datetime.datetime.now(datetime.UTC)

    tz_data = google_maps.get_tz_offset(maps_api_key, location, utc_now)
    if tz_data['status'] != 'OK':
        return tz_data

    tide_data = worldtides_info.fetch_tides(tides_api_key, location)
    if tide_data['status'] != 200:
        return tide_data

    tides = []
    for tide in tide_data['extremes']:
        dt = tide['dt']
        date = tide['date']
        height = tide['height']
        type = tide['type']

        # is the tide in the past?
        tide_time = datetime.datetime.fromtimestamp(dt, datetime.timezone.utc)
        if tide_time < utc_now:
            prior = 'prior'
        else:
            prior = 'future'

        tides.append({
            'type': type,
            'date': tide_time.strftime(utils.MM_DD_DATE_FORMAT),
            'day': tide_time.strftime(utils.DAY_FORMAT),
            'time': tide_time.strftime(utils.TIME_FORMAT),
            'prior': prior,
            'iso-date': date,
            'height': height
        })

    values = {
        'status': (tide_data['status']),
        'req_timestamp': utils.offset_timestamp(utc_now, tz_data['offset']),
        'req_lat': (location[0]), 'req_lon': (location[1]),
        'resp_lat': (tide_data['responseLat']), 'resp_lon': (tide_data['responseLon']),
        'station': (tide_data['station']),
        'req_tz_offset': tz_data['offset'],
        'req_tz': tz_data['name'],
        'tides': tides,
        'wti_copyright': tide_data['copyright'],
        'station_tz': tide_data['timezone']
    }

    return values


def get_station(lat, lon):
    stations = Station.query(Station.lat == lat, Station.lon == lon).fetch(1)
    if len(stations) != 0:
        return stations[0]
    else:
        return None


def get_stations():
    stations = Station.query()
    out_stations = []
    for station in stations:
        out_stations.append({
            'name': station.name,
            'loc': {
                'lat': station.lat,
                'lon': station.lon
            },
            'id': station.key.id()
        })

    return {
        'status': 'OK',
        'station_count': stations.count(),
        'stations': out_stations
    }


def refresh_stations():
    station_data = worldtides_info.fetch_stations(tides_api_key)

    if station_data['status'] != 'OK':
        return station_data

    for found_station in station_data['stations']:
        new_station = Station(
            id=found_station['id'],
            lat=found_station['lat'],
            lon=found_station['lon'],
            name=found_station['name'],
        )
        new_station.put()

    return get_stations()
