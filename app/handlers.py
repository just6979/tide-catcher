import datetime

import webapp2
from google.appengine.ext import ndb

import datastore
import google_maps_api as maps_api
import templates
import utils
import worldtides_info_api as tides_api


class TidesHandler(webapp2.RequestHandler):
    def get(self):
        # TODO: cache & reuse requests for the same station within 12 hours
        # TODO: handle incoming location requests
        # Lynn, MA
        req_lat = 42.478744
        req_lon = -71.001188
        req_loc = (req_lat, req_lon)

        # right now in UTC as naive datetime
        utc_now = datetime.datetime.utcnow()
        # minus 12 hours to make sure we get the last tide (maybe last 2)
        utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

        station_loc = datastore.nearest_station_loc(req_loc)

        # check if this location was cached in the last 12 hours
        values = datastore.check_cache(station_loc, utc_minus_12)

        if not values:
            # if this location wasn't cached
            tz_data = maps_api.get_tz_offset(req_loc, utc_now)

            status = tz_data['status']
            if status != 'OK':
                values = tz_data
                template_file = "error.html"
            else:
                tide_data = tides_api.fetch_tides(
                    req_loc, utc_minus_12, utc_now, tz_data['offset']
                )

                status = tide_data['status']
                if status == 'OK':
                    start_timestamp = utils.to_nearest_minute(
                        utils.offset_timestamp(utc_now, tz_data['offset'])
                    )
                    req_timestamp = {
                        'date': start_timestamp.strftime(utils.DATE_FORMAT),
                        'time': start_timestamp.strftime(utils.TIME_FORMAT),
                        'day': start_timestamp.strftime(utils.DAY_FORMAT),
                    }
                    values = {
                        'req_timestamp': req_timestamp,
                        'req_lat': req_lat,
                        'req_lon': req_lon,
                        'resp_lat': tide_data['lat'],
                        'resp_lon': tide_data['lon'],
                        'resp_station': tide_data['station'],
                        'tz_offset': tz_data['offset'],
                        'tz_name': tz_data['name'],
                        'tides': tide_data['tides'],
                    }
                    datastore.save_to_cache((tide_data['lat'], tide_data['lon']), utc_now)
                    template_file = "tides.html"
                else:
                    values = tide_data
                    template_file = "error.html"

            templates.render(self, template_file, values)


class StationsHandler(webapp2.RequestHandler):
    def get(self):
        stations = datastore.Station.query()
        values = {
            'station_count': stations.count(),
            'stations': stations
        }
        templates.render(self, 'stations.html', values)


class StationRefreshHandler(webapp2.RequestHandler):
    def get(self):
        station_data = tides_api.fetch_stations()

        if station_data['status'] != 'OK':
            values = station_data
            template_file = "error.html"
            templates.render(self, template_file, values)
        else:
            for station in station_data['stations']:
                new_station = datastore.Station(
                    id=int(station['id'][5:]),
                    loc=(ndb.GeoPt(station['lat'], station['lon'])),
                    name=station['name'],
                )
                new_station.put()
            return self.redirect('/stations')
