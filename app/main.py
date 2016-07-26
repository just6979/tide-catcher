import os

import jinja2
import webapp2
from google.appengine.ext import ndb

import google_maps as maps_api
import worldtides_info as tides_api
from datastore import Station, check_cache, nearest_station_loc, save_to_cache
from test_handlers import BaseTestHandler, ErrorTestHandler, \
    StationsTestHandler, TestHandler, TidesTestHandler
from utils import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

tides_api_key = tides_api.get_api_key()
maps_api_key = maps_api.get_api_key()


class TidesHandler(webapp2.RequestHandler):
    def get(self):
        # TODO: cache & reuse requests for the same station within 12 hours
        # TODO: handle incoming location requests (Full page response or HttpReq and JSON?)
        # Lynn, MA
        req_lat = 42.478744
        req_lon = -71.001188
        req_loc = (req_lat, req_lon)

        # right now in UTC as naive datetime
        utc_now = datetime.datetime.utcnow()
        # minus 12 hours to make sure we get the last tide (maybe last 2)
        utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

        station_loc = nearest_station_loc(req_loc)

        # check if this location was cached in the last 12 hours
        values = check_cache(station_loc, utc_minus_12)

        if not values:
            # if this location wasn't cached
            tz, tz_url = maps_api.fetch_and_decode(
                maps_api_key, req_loc, utc_now
            )

            status = tz['status']
            if status != 'OK':
                values = {
                    'module': 'Google Maps API',
                    'status': tz['status'],
                    'error': tz['error'],
                    'msg': tz['msg'],
                }
                template = JINJA_ENVIRONMENT.get_template("error.html")
                print(status)
                self.response.write(template.render(values))
                return

            tides, tides_url = tides_api.fetch_and_decode(
                tides_api_key, req_loc, utc_minus_12, utc_now, tz['offset']
            )

            status = tides['status']
            if status == 'OK':
                start_timestamp = to_nearest_minute(
                    offset_timestamp(utc_now, tz['offset'])
                )
                req_timestamp = {
                    'date': start_timestamp.strftime(DATE_FORMAT),
                    'time': start_timestamp.strftime(TIME_FORMAT),
                    'day': start_timestamp.strftime(DAY_FORMAT),
                }
                values = {
                    'copyright': tides['copyright'],
                    'req_timestamp': req_timestamp,
                    'req_lat': req_lat,
                    'req_lon': req_lon,
                    'resp_lat': tides['lat'],
                    'resp_lon': tides['lon'],
                    'resp_station': tides['station'],
                    'tz_offset': tz['offset'],
                    'tz_name': tz['name'],
                    'tides': tides['tides'],
                }

                save_to_cache((tides['lat'], tides['lon']), utc_now)

                template = JINJA_ENVIRONMENT.get_template("tides.html")
                self.response.write(template.render(values))
            else:
                values = {
                    'module': 'World Tides API',
                    'status': tides['status'],
                    'error': tides['error'],
                    'msg': tides['msg'],
                }
                template = JINJA_ENVIRONMENT.get_template("error.html")
                self.response.write(template.render(values))


class StationsHandler(webapp2.RequestHandler):
    def get(self):
        stations = Station.query()

        values = {
            'station_count': stations.count(),
            'stations': stations
        }

        template = JINJA_ENVIRONMENT.get_template("stations.html")
        self.response.write(template.render(values))


class StationRefreshHandler(webapp2.RequestHandler):
    def get(self):
        (stations_url, stations) = tides_api.fetch_stations(tides_api_key)

        for station in stations:

            new_station = Station(
                id=int(station['id'][5:]),
                loc=(ndb.GeoPt(station['lat'], station['lon'])),
                name=station['name'],
            )
            new_station.put()

        return self.redirect('/stations')


app = webapp2.WSGIApplication([
    ('/', TidesHandler),
    ('/stations', StationsHandler),
    ('/refresh-stations', StationRefreshHandler),
    ('/test', TestHandler),
    ('/test/base', BaseTestHandler),
    ('/test/error', ErrorTestHandler),
    ('/test/tides', TidesTestHandler),
    ('/test/stations', StationsTestHandler),
], debug=True)
