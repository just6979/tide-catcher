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
        url, response = tides.fetch(api_key)
        output += url + '\n'
        output += tides.decode(response)
        self.response.write(template % output)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
