from google.appengine.ext import ndb


class TideData(ndb.Model):
    req_loc = ndb.StringProperty(indexed=True)
    req_time = ndb.TimeProperty(indexed=False, required=True)
    tide_data = ndb.JsonProperty(indexed=False, required=True)


class LocationMatch(ndb.Model):
    req_location = ndb.StringProperty(indexed=True)
    resp_location = ndb.StringProperty(indexed=False, required=True)


class Station(ndb.Model):
    loc = ndb.GeoPtProperty(indexed=True)
    name = ndb.StringProperty(required=True)


def nearest_station_loc(req_loc):
    return req_loc


def save_nearest_station(req_loc):
    pass


def check_cache(location, save_time):
    return False


def save_to_cache(location, utc_now):
    pass
