import json

import webapp2

import templates
import tides


class IndexHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(open('templates/index.mustache').read())


class TidesHandler(webapp2.RequestHandler):
    def get(self):
        templates.render(self, 'tides.html', {})


class StationsHandler(webapp2.RequestHandler):
    def get(self):
        templates.render(self, 'stations.html', {})


class StationRefreshHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.refresh_stations()

        if values['status'] == 'OK':
            return self.redirect('/stations')
        else:
            template_file = 'error.html'
            return templates.render(self, template_file, values)


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
                self.response.write(json.dumps(values))
        else:
            self.response.write(u'No Location Given')
            self.response.set_status(404)


class JSONStationsHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.get_stations()
        self.response.write(json.dumps(values))
