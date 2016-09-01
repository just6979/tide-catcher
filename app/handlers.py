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


class TidesLynnHandler(webapp2.RequestHandler):
    def get(self):
        # Lynn, MA
        req_lat = 42.478744
        req_lon = -71.001188

        values = tides.for_location((req_lat, req_lon))

        if values['status'] == 'OK':
            template_file = 'tides_lynn.html'
        else:
            template_file = 'error.html'

        templates.render(self, template_file, values)
