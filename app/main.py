import calendar
import os
import time

import jinja2
import webapp2
from google.appengine.ext import ndb

import google_maps as maps
import worldtides_info as tides

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

api_key = tides.get_api_key()


class TideData(ndb.Model):
    result_location = ndb.StringProperty(indexed=True)
    tide_data = ndb.JsonProperty(indexed=False, required=True)


class LocationMatch(ndb.Model):
    query_location = ndb.StringProperty(indexed=True)
    result_location = ndb.StringProperty(indexed=False, required=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        # Lynn, MA
        location = (42.478744, -71.001188)
        # right now in UTC as seconds since epoch
        start_time = calendar.timegm(time.gmtime()),

        tz_offset, tz_name = maps.get_tz_offset(location, start_time)

        query_url, response = tides.fetch(location, start_time, api_key)
        data = tides.decode(response, tz_offset)

        if 'error' in data:
            values = {
                'error': data['error'],
                'data': data['data'],
            }
        else:
            values = {
                'query_url': query_url,
                'copyright': data['copyright'],
                'lat': data['lat'],
                'lon': data['lon'],
                'tz_offset': tz_offset,
                'tz_name': tz_name,
                'tides': data['tides'],
            }

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(values))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
