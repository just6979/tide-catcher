from flask import Flask, request

from src import tides

app = Flask(__name__)


@app.get('/')
def get():
    return open('templates/index.mustache').read()


@app.get('/json/tides/by-location/<location>')
def json_tides_by_location(location: str):
    location_split = location.split(',')
    if len(location_split) != 2:
        return ['Bad Location Given']

    return tides.for_location(location_split)


@app.get('/json/tides/by-station/<station>')
def json_tides_by_station(station: str):
    return tides.for_station(station)


@app.get('/json/stations')
def json_stations():
    return tides.get_stations()


@app.get('/json/stations/refresh')
def refresh_stations():
    return tides.refresh_stations()


@app.get('/json/station/by-id/<station_id>')
def json_station_by_id(station_id: str):
    return tides.station_by_id(station_id)


@app.get('/json/station/by-nearest/<location>')
def json_station_by_nearest(location: str):
    return tides.station_by_nearest(location)
