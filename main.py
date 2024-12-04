from flask import Flask, request
from google.cloud import ndb

from src import tides

client = ndb.Client()


def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


app = Flask(__name__)
app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)


@app.get('/')
def get():
    return open('templates/index.mustache').read()


@app.get('/json/tides')
def json_tides():
    location = request.args.get(u'loc', None)
    if location:
        try:
            req_lat, req_lon = location.split(',')
        except ValueError as e:
            return [u'Bad Location: "%s", %s' % (location, e)], 404
        except Exception as e:
            return [u'Bad Location: "%s", %s' % (location, e)], 404
        else:
            values = tides.for_location((req_lat, req_lon))
            if values['status'] == 'OK':
                return values
            else:
                return values, 404
    else:
        return u'No Location Given', 404


@app.get('/json/stations')
def json_stations():
    values = tides.get_stations()
    return values


@app.get('/json/refresh-stations')
def refresh_stations():
    values = tides.refresh_stations()
    return values
