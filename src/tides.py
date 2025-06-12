import os
import zoneinfo
from datetime import datetime, timezone

from google.cloud import datastore

from src import utils
from . import worldtides_info

_module = 'Tides'

tides_api_key = os.environ['WORLDTIDES_INFO_API_KEY']


def for_location(location: list):

    utc_now = datetime.now(timezone.utc)
    print(utc_now)
    print(utc_now.tzinfo)

    tide_data = worldtides_info.fetch_tides(tides_api_key, location)
    if tide_data['status'] != 200:
        return tide_data

    tz = zoneinfo.ZoneInfo(tide_data['timezone'])
    print(tz)
    local_now = utc_now.astimezone(tz)
    print(local_now)
    print(local_now.tzinfo)

    tides = []
    for tide in tide_data['extremes']:
        dt = tide['dt']
        date = tide['date']
        height = tide['height']
        type = tide['type']

        # is the tide in the past?
        tide_time = datetime.fromisoformat(date)
        if tide_time < local_now:
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
        'req_timestamp': local_now.strftime('%a, %d %b %Y %H:%M:%S %Z'),
        'req_lat': (location[0]), 'req_lon': (location[1]),
        'resp_lat': (tide_data['responseLat']), 'resp_lon': (tide_data['responseLon']),
        'station': (tide_data['station']),
        'tides': tides,
        'wti_copyright': tide_data['copyright'],
        'station_tz': tide_data['timezone']
    }

    return values


def for_station(station):
    return {}


def get_stations():
    client = datastore.Client()
    query = client.query(kind='Station')
    stations = list(query.fetch())

    out_stations = []
    station_data: datastore.Entity
    for station_data in stations:
        station_id = station_data.key.name
        next_station = build_station(station_id, station_data)
        out_stations.append(next_station)
    return {
        'status': 'OK',
        'station_count': len(out_stations),
        'stations': out_stations
    }


def refresh_stations():
    station_data = worldtides_info.fetch_stations(tides_api_key)

    if station_data['status'] != 'OK':
        return station_data

    client = datastore.Client()
    for found_station in station_data['stations']:
        station_id = found_station['id']
        key = client.key('Station', station_id)
        station = datastore.Entity(key)
        org, org_id = station_id.split(':')
        station.update({
            'org': org,
            'org_id': org_id,
            'name': found_station['name'],
            'lat': found_station['lat'],
            'lon': found_station['lon']
        })
        client.put(station)

    return get_stations()


def station_by_id(station_id):
    client = datastore.Client()
    key = client.key('Station', station_id)
    station_data = client.get(key)
    found_station = build_station(station_id, station_data)
    return {
        'status': 'OK',
        'station': (found_station)
    }


def station_by_nearest(location):
    stations = worldtides_info.fetch_nearest_stations(tides_api_key, location.split(','))
    station_data = stations['stations'][0]
    found_station = build_station(station_data['id'], station_data)
    return {
        'status': 'OK',
        'station': found_station
    }


def build_station(station_id, station_data):
    if not station_data.get('org') or not station_data.get('org_id'):
        org, org_id = station_id.split(':')
    else:
        org = station_data['org']
        org_id = station_data['org_id']
    return {
        'id': station_id,
        'org': org,
        'org_id': org_id,
        'name': station_data['name'],
        'lat': station_data['lat'],
        'lon': station_data['lon'],
        'noaa': 'NOAA' in org,
    }
