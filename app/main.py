import os

import jinja2
import webapp2
from google.appengine.ext import ndb

import worldtides_info as tides

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

api_key = tides.get_api_key()


class LocationMatch(ndb.Model):
    query_location = ndb.StringProperty(indexed=True)
    result_location = ndb.StringProperty(indexed=False, required=True)


class TideData(ndb.Model):
    result_location = ndb.StringProperty(indexed=True)
    tide_data = ndb.JsonProperty(indexed=False, required=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        query_url, response = tides.fetch(api_key)
        data = tides.decode(response)

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
                'lon': data['lat'],
                'tides': data['tides'],
            }

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(values))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
