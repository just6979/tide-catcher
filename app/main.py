#!/usr/bin/env python

import calendar
import json
import time
import urllib2

import webapp2

api_key = open("api_key.txt").readline().strip()

template = """
<html>
<head>
<title>tide-cacher</title>
</head>
<body>
<pre>
%s
</pre>
</body>
</html>
"""


def fetch_and_decode():
    out = ""

    request_url = "https://www.worldtides.info/api?{options}&lat={lat}&lon={lon}&start={start}&key={key}\n".format(
        options="extremes",
        # Lynn, MA
        lat=42.4787444,
        lon=-71.0011876,
        # right now in UTC as seconds since epoch
        start=calendar.timegm(time.gmtime()),
        key=api_key
    )
    out += request_url

    response = urllib2.urlopen(request_url)
    data = json.loads(response.read().decode())
    # out += data

    out += data['copyright'] + "\n"

    out += "Location: %s, %s\n" % (data['responseLat'], data['responseLon'])

    for tide in data['extremes']:
        out += "{type}\t{time}\n".format(
            type=tide['type'],
            time=time.asctime(time.localtime(tide['dt']))
        )

    return out


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template % fetch_and_decode())


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
