from flask import Flask, request

from src import tides

app = Flask(__name__)


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
