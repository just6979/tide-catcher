import datetime
import logging
import os

import jinja2
import webapp2
from google.appengine.ext import ndb

import google_maps as maps_api
import worldtides_info as tides_api
from utils import adjusted_datetime, TIME_FORMAT, DATE_FORMAT

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
        # TODO: handle incoming location requests (Full page response or HttpReq and JSON?)
        # Lynn, MA
        request_lat = 42.478744
        request_lon = -71.001188
        request_location = (request_lat, request_lon)

        # right now in UTC as naive datetime
        utc_now = datetime.datetime.utcnow()
        # minus 12 hours to make sure we get the last tide (maybe last 2)
        utc_minus_12 = utc_now + datetime.timedelta(hours=-12)

        (tides, tides_url), (tz, tz_url) = tides_api.fetch_and_decode(
            tides_api_key, maps_api_key, request_location, utc_minus_12, utc_now
        )

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
            logging.info(tz_url)
            logging.info(tides_url)
            adjusted_start_time = adjusted_datetime(utc_minus_12, tz['offset'])
            req_time = "%s %s" % (adjusted_start_time.strftime(DATE_FORMAT), adjusted_start_time.strftime(TIME_FORMAT))
            values = {
                'copyright': tides['copyright'],
                'req_time': req_time,
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
