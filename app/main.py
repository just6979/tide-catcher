import webapp2

import handlers
import json_handlers
import test_handlers

app = webapp2.WSGIApplication([

    ('/', handlers.TidesHandler),
    ('/stations', handlers.StationsHandler),
    ('/refresh-stations', handlers.StationRefreshHandler),

    # the old default: non-AJAX, non geolocated
    ('/lynn', handlers.TidesLynnHandler),

    ('/json/tides', json_handlers.JSONTidesHandler),
    ('/json/stations', json_handlers.JSONStationsHandler),

    ('/test', test_handlers.TestHandler),
    ('/test/base', test_handlers.BaseTestHandler),
    ('/test/error', test_handlers.ErrorTestHandler),
    ('/test/tides', test_handlers.TidesTestHandler),
    ('/test/stations', test_handlers.StationsTestHandler),

], debug=True)

