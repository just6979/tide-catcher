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
    if not location:
        return ['No Location Given']

    location_split = location.split(',')
    if len(location_split) != 2:
        return ['Bad Location Given']

    return tides.for_location(location_split)


@app.get('/json/stations')
def json_stations():
    return tides.get_stations()


@app.get('/json/refresh-stations')
def refresh_stations():
    return tides.refresh_stations()
