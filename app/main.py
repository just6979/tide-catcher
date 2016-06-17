import os

import jinja2
import webapp2

import worldtides_info as tides

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# template = """
# <html>
# <head>
# <title>tide-cacher</title>
# </head>
# <body>
# <pre>
# %s
# </pre>
# </body>
# </html>
# """

api_key = tides.get_api_key()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        query_url, response = tides.fetch(api_key)
        data = tides.decode(response)

        if 'error' in data:
            values = {
                'error': data['error'],
                'data': data['data'],
            }
        else:
            values = {
                'query_url': query_url,
                'copyright': data['copyright'],
                'location': data['location'],
                'tides': data['tides'],
            }

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(values))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
