from flask import Flask, request

from . import tides

app = Flask(__name__)


@app.get('/.*')
def get():
    return open('templates/index.mustache').read()


app.get('/json/tides')
def json_tides():
    location = request.get(u'loc', default_value=None)
    if location:
        try:
            req_lat, req_lon = location.split(',')
        except ValueError as e:
            return u'Bad Location: "%s", %s' % (location, e), 404
        except Exception as e:
            return u'Bad Location: "%s", %s' % (location, e), 404
        else:
            values = tides.for_location((req_lat, req_lon))
            if values['status'] == 'OK':
                return values
            else:
                return values, 404
    else:
        return u'No Location Given', 404


app.get('/json/stations')
def json_stations():
    values = tides.get_stations()
    return values


app.get('/json/refresh-stations')
def refresh_stations():
    values = tides.refresh_stations()
    return values
