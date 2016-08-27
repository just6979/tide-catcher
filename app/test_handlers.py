import webapp2

import templates

class TestHandler(webapp2.RequestHandler):
    # show the base template, for reference
    def get(self):
        values = {
            'data': '''
<p>
Template testing:<br/>
<a href="/test/base">Base</a>
<a href="/test/error">Error</a>
<a href="/test/tides">Tides</a>
<a href="/test/stations">Stations</a>
<p>
            '''
        }
        templates.render(self, 'base.html', values)


class BaseTestHandler(webapp2.RequestHandler):
    # show the base template, for reference
    def get(self):
        values = {
            'data': 'Base Test'}
        templates.render(self, 'base.html', values)


class TidesTestHandler(webapp2.RequestHandler):
    # show the error template, for reference
    def get(self):
        values = {
            'copyright': 'copyright',
            'req_timestamp': {'day': 'day', 'date': 'date', 'time': 'time'},
            'req_lat': 0.0,
            'req_lon': 0.0,
            'resp_lat': 0.0,
            'resp_lon': 0.0,
            'resp_station': 'tides[station]',
            'tz_offset': 0,
            'tz_name': 'tz[name]',
            'tides': [
                {
                    'type': 'low',
                    'date': 'timestamp.strftime(DATE_FORMAT)',
                    'day': 'timestamp.strftime(DAY_FORMAT)',
                    'time': 'timestamp.strftime(TIME_FORMAT)',
                    'prior': 'prior',

                },
                {
                    'type': 'high',
                    'date': 'timestamp.strftime(DATE_FORMAT)',
                    'day': 'timestamp.strftime(DAY_FORMAT)',
                    'time': 'timestamp.strftime(TIME_FORMAT)',
                    'prior': 'future',
                },
            ]
        }
        templates.render(self, 'tides_lynn.html', values)


class ErrorTestHandler(webapp2.RequestHandler):
    # show the error template, for reference
    def get(self):
        values = {'error': 'Test Error'}
        templates.render(self, 'error.html', values)


class StationsTestHandler(webapp2.RequestHandler):
    # show the error template, for reference
    def get(self):
        values = {
            'station_count': 1,
            'stations': [{
                'name': 'Test Station',
                'loc': {'lat': 0.0, 'lon': 0.0},
                'id': '0000000'
            }]
        }
        templates.render(self, 'stations.html', values)
