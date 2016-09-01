import datetime

import google_maps_api as maps_api
import utils
import worldtides_info_api as tides_api
from datastore import Station


def for_location(req_loc):
    req_lat, req_lon = req_loc

    # right now in UTC as naive datetime
    utc_now = datetime.datetime.utcnow()
    # minus 12 hours to make sure we get the last tide (maybe last 2)
    utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

    # if this location wasn't cached
    tz_data = maps_api.get_tz_offset(req_loc, utc_now)

    status = tz_data['status']
    if status != 'OK':
        # error
        values = tz_data
    else:
        # timezone data is good, fetch & check tide data
        tide_data = tides_api.fetch_tides(
            req_loc, utc_minus_12, utc_now, tz_data['offset']
        )

        status = tide_data['status']
        if status == 'OK':
            # tide data is good

            # get station data
            resp_lat = tide_data['responseLat']
            resp_lon = tide_data['responseLon']
            station = get_station(resp_lat, resp_lon)
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
                'req_lat': req_lat, 'req_lon': req_lon,
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
    # should only ever be one station at a given (lat,lon)
    return Station.query(Station.lat == lat, Station.lon == lon).fetch(1)[0]


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
    station_data = tides_api.fetch_stations()

    if station_data['status'] != 'OK':
        values = station_data
    else:
        values = {
            'status': 'OK'
        }
        for station in station_data['stations']:
            new_station = Station(
                id=int(station['id'][5:]),
                lat=station['lat'],
                lon=station['lon'],
                name=station['name'],
            )
            new_station.put()
    return values
