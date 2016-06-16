import webapp2

import worldtides_info as tides

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

api_key = tides.get_api_key()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        output = ""
        url, data = tides.fetch(api_key)
        output += url + '\n'
        output += tides.decode(data)
        self.response.write(template % output)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
