import webapp2

import handlers

app = webapp2.WSGIApplication([
    ('/', handlers.IndexHandler),
    ('/tides', handlers.TidesHandler),

    ('/stations', handlers.StationsHandler),
    ('/refresh-stations', handlers.StationRefreshHandler),

    ('/json/tides', handlers.JSONTidesHandler),
    ('/json/stations', handlers.JSONStationsHandler),
], debug=True)
