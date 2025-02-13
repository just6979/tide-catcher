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
            # TODO: round times to nearest minute
            'time': tide_time.strftime(utils.TIME_FORMAT),
            'prior': prior,
            'iso-date': date,
            'height': height
        })

    # get station data
    resp_lat = tide_data['responseLat']
    resp_lon = tide_data['responseLon']
    station = get_station(resp_lat, resp_lon)
    if station is None:
        return utils.error_builder(_module, 'ERR', "No Valid Stations Found.")
    station_name = station.name
    station_id = station.key.id()

    start_timestamp = utils.to_nearest_minute(
        utils.offset_timestamp(utc_now, tz_data['offset'])
    )
    req_timestamp = {
        'date': start_timestamp.strftime(utils.YYYY_MM_DD_DATE_FORMAT),
        'time': start_timestamp.strftime(utils.TIME_FORMAT),
        'day': start_timestamp.strftime(utils.DAY_FORMAT),
    }
    values = {
        'status': (tide_data['status']),
        'req_timestamp': req_timestamp,
        'req_lat': (location[0]), 'req_lon': (location[1]),
        'resp_lat': resp_lat, 'resp_lon': resp_lon,
        'station_id': station_id,
        'station_name': station_name,
        'tz_offset': tz_data['offset'],
        'tz_name': tz_data['name'],
        'tides': tides,
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
