import datetime

from google.appengine.ext import ndb

import datastore
import google_maps_api as maps_api
import utils
import worldtides_info_api as tides_api


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
            # tides data is good
            start_timestamp = utils.to_nearest_minute(
                utils.offset_timestamp(utc_now, tz_data['offset'])
            )
            req_timestamp = {
                'date': start_timestamp.strftime(utils.YYYY_MM_DD_DATE_FORMAT),
                'time': start_timestamp.strftime(utils.TIME_FORMAT),
                'day': start_timestamp.strftime(utils.DAY_FORMAT),
            }
            values = {'status': status, 'req_timestamp': req_timestamp,
                      'req_lat': req_lat, 'req_lon': req_lon,
                      'resp_lat': tide_data['lat'],
                      'resp_lon': tide_data['lon'],
                      'resp_station': tide_data['station'],
                      'tz_offset': tz_data['offset'],
                      'tz_name': tz_data['name'], 'tides': tide_data['tides'],}
        else:
            # error
            values = tide_data

    return values


def get_stations():
    stations = datastore.Station.query()
    out_stations = []
    for station in stations:
        out_stations.append({
            'name': station.name,
            'loc': {
                'lat': station.loc.lat,
                'lon': station.loc.lon
            },
            'id': station.id
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
            new_station = datastore.Station(
                id=int(station['id'][5:]),
                loc=(ndb.GeoPt(station['lat'], station['lon'])),
                name=station['name'],
            )
            new_station.put()
    return values
