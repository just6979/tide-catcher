import json

import webapp2

from . import tides


class IndexHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(open('templates/index.mustache').read())


class JSONTidesHandler(webapp2.RequestHandler):
    def get(self):
        location = self.request.get(u'loc', default_value=None)
        if location:
            try:
                req_lat, req_lon = location.split(',')
            except ValueError as e:
                self.response.write(
                    u'Bad Location: "%s", %s' % (location, e.message)
                )
                self.response.set_status(404)
            except Exception as e:
                self.response.write(
                    u'Bad Location: "%s", %s' % (location, e.message)
                )
                self.response.set_status(404)
            else:
                values = tides.for_location((req_lat, req_lon))
                if values['status'] == 'OK':
                    self.response.write(json.dumps(values))
                else:
                    self.response.write(json.dumps(values))
                    self.response.set_status(404)
        else:
            self.response.write(u'No Location Given')
            self.response.set_status(404)


class JSONStationsHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.get_stations()
        self.response.write(json.dumps(values))


class JSONStationRefreshHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.refresh_stations()
        self.response.write(json.dumps(values))


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/json/tides', JSONTidesHandler),
    ('/json/stations', JSONStationsHandler),
    ('/json/refresh-stations', JSONStationRefreshHandler),
], debug=True)
