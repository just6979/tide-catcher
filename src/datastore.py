from google.cloud import ndb


class TideData(ndb.Model):
    req_loc = ndb.StringProperty()
    req_time = ndb.TimeProperty(indexed=False, required=True)
    tide_data = ndb.JsonProperty(indexed=False, required=True)


class LocationMatch(ndb.Model):
    req_location = ndb.StringProperty()
    resp_location = ndb.StringProperty(required=True)


class Station(ndb.Model):
    lat = ndb.FloatProperty(indexed=True)
    lon = ndb.FloatProperty(indexed=True)
    name = ndb.StringProperty(required=True)


def nearest_station_loc(req_loc):
    return req_loc


def save_nearest_station(req_loc):
    pass


def check_cache(location, save_time):
    return False


def save_to_cache(location, utc_now):
    pass
