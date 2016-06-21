import calendar
import os
import time

import jinja2
import webapp2
from google.appengine.ext import ndb

import google_maps as maps_api
import worldtides_info as tides_api

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

tides_api_key = tides_api.get_api_key()
maps_api_key = maps_api.get_api_key()


class TideData(ndb.Model):
    result_location = ndb.StringProperty(indexed=True)
    tide_data = ndb.JsonProperty(indexed=False, required=True)


class LocationMatch(ndb.Model):
    query_location = ndb.StringProperty(indexed=True)
    result_location = ndb.StringProperty(indexed=False, required=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        # Lynn, MA
        request_lat = 42.478744
        request_lon = -71.001188
        request_location = (request_lat, request_lon)

        # right now in UTC as seconds since epoch
        start_time = calendar.timegm(time.gmtime()),

        tz_url, tz_response = maps_api.fetch(maps_api_key, request_location, start_time)
        tz = maps_api.decode(tz_response)

        tides_url, tides_response = tides_api.fetch(tides_api_key, request_location, start_time)
        tides = tides_api.decode(tides_response, tz['offset'])

        if 'error' in tz:
            values = {
                'error': tz['error'],
                'data': tz['data'],
            }
        elif 'error' in tides:
            values = {
                'error': tides['error'],
                'data': tides['data'],
            }
        else:
            values = {
                'copyright': tides['copyright'],
                'req_lat': request_lat,
                'req_lon': request_lon,
                'resp_lat': tides['lat'],
                'resp_lon': tides['lon'],
                'resp_station': tides['station'],
                'tz_offset': tz['offset'],
                'tz_name': tz['name'],
                'tides': tides['tides'],
            }

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(values))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
