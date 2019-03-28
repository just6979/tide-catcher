import ConfigParser

config = ConfigParser.ConfigParser()
config.read("config.ini")

google_maps_api_key = config.get("api_keys", "google_maps")
worldtides_info_api_key = config.get("api_keys", "worldtides_info")
