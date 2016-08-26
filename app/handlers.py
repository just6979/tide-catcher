import webapp2

import templates
import tides


class TidesHandler(webapp2.RequestHandler):
    def get(self):
        # TODO: cache & reuse requests for the same station within 12 hours
        # TODO: handle incoming location requests
        # Lynn, MA
        req_lat = 42.478744
        req_lon = -71.001188

        values = tides.for_location((req_lat, req_lon))

        if values['status'] == 'OK':
            template_file = 'tides.html'
        else:
            template_file = 'error.html'

        templates.render(self, template_file, values)


class StationsHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.get_stations()

        if values['status'] == 'OK':
            template_file = 'stations.html'
        else:
            template_file = 'error.html'

        templates.render(self, template_file, values)


class StationRefreshHandler(webapp2.RequestHandler):
    def get(self):
        values = tides.refresh_stations()

        if values['status'] == 'OK':
            return self.redirect('/stations')
        else:
            template_file = 'error.html'
            return templates.render(self, template_file, values)


class TidesAJAXHandler(webapp2.RequestHandler):
    def get(self):
        # TODO: cache & reuse requests for the same station within 12 hours
        # TODO: handle incoming location requests
        # Lynn, MA
        req_lat = 42.478744
        req_lon = -71.001188

        values = tides.for_location((req_lat, req_lon))

        if values['status'] == 'OK':
            template_file = 'tides_ajax.html'
        else:
            template_file = 'error.html'

        templates.render(self, template_file, values)
