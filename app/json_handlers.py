import json

import webapp2

import tides


class JSONTidesHandler(webapp2.RequestHandler):
    def get(self):
        # Lynn, MA
        # req_lat, req_lon = 42.478744, -71.001188

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
                self.response.out.write(json.dumps(values))
        else:
            self.response.write(u'No Location Given')
            self.response.set_status(404)


class JSONStationsHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.get_stations()
        self.response.out.write(json.dumps(values))
