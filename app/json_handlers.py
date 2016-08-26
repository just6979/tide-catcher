import json

import webapp2

import tides


class JSONTidesHandler(webapp2.RequestHandler):
    def get(self):
        # Lynn, MA
        # req_lat, req_lon = 42.478744, -71.001188

        location = self.request.get(u'loc')
        req_lat, req_lon = location.split(u',')
        req_loc = (req_lat, req_lon)

        values = tides.for_location(req_loc)
        self.response.out.write(json.dumps(values))


class JSONStationsHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.get_stations()
        self.response.out.write(json.dumps(values))
