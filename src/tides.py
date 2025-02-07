import datetime
import os

from . import utils
from .datastore import Station
from .wrapper import google_maps, worldtides_info

_module = 'Tides'

maps_api_key = os.environ['GOOGLE_MAPS_API_KEY']
tides_api_key = os.environ['WORLDTIDES_INFO_API_KEY']


def for_location(location_split: list):
    lattitude: str
    logitude: str

    lattitude, logitude = location_split

    # right now in UTC as naive datetime
    utc_now = datetime.datetime.now(datetime.UTC)
    # minus 12 hours to make sure we get the last tide (maybe last 2)
    utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

    # if this location wasn't cached
    tz_data = google_maps.get_tz_offset(maps_api_key, location_split, utc_now)

    status = tz_data['status']
    if status != 'OK':
        # error
        values = tz_data
    else:
        # timezone data is good, fetch & check tide data
        tide_data = worldtides_info.fetch_tides(
            tides_api_key, location_split, utc_minus_12, utc_now, tz_data['offset']
        )

        status = tide_data['status']
        if status == 'OK':
            # tide data is good

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
                'status': status,
                'req_timestamp': req_timestamp,
                'req_lat': lattitude, 'req_lon': logitude,
                'resp_lat': resp_lat, 'resp_lon': resp_lon,
                'station_id': station_id,
                'station_name': station_name,
                'tz_offset': tz_data['offset'],
                'tz_name': tz_data['name'],
                'tides': tide_data['tides'],
            }
        else:
            # error
            values = tide_data

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
