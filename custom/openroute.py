import requests

from apps.bushelper import Point


class OpenrouteDirections:
    """Makes request to Openroute directions service"""

    def __init__(self, origin, destination):
        self.url = 'https://api.openrouteservice.org/directions'
        # self.api_key = open('/home/daniel/openroute_api').read()
        self.api_key = '5b3ce3597851110001cf6248ef4bb898eeb44f51896bc7d885e18685'  # TODO to nie mzoe byc na sztywno
        self.format = "geojson"
        self.coordinates = None
        self.params = {
            'api_key': self.api_key,
            'format': self.format,
        }
        self.origin = origin
        self.destination = destination

    @staticmethod
    def get_parsed_coordinates(points):
        coordinates = []
        for point in points:
            if isinstance(point, BusStop) or isinstance(point, Point):
                long = str(point.longtitude)
                lat = str(point.latitude)
                full_coordinates = ",".join([long, lat])
                coordinates.append(full_coordinates)
            elif isinstance(point, list):
                full_coordinates = ','.join(map(str, [point[0], point[1]]))
                coordinates.append(full_coordinates)
        return '|'.join(coordinates)

    def set_coordinates(self, origin, destination):
        points = [origin, destination]
        self.coordinates = self.get_parsed_coordinates(points)

    def add_params(self, **kwargs):
        for key in kwargs:
            key = str(key)
            self.params[key] = kwargs[key]

    def get_api_data(self, profile, **kwargs):
        """Available args reference:
        https://openrouteservice.org/documentation/#/reference/directions/directions/directions-service"""

        self.set_coordinates(self.origin, self.destination)

        self.params['coordinates'] = self.coordinates
        self.params['profile'] = profile
        self.params['instructions'] = 'false'
        if kwargs:
            self.add_params(**kwargs)

        api_request = requests.get(self.url, params=self.params)
        api_response = api_request.text

        return api_response

    def get_custom_walking_api(self, current_location, **kwargs):

        origin = current_location
        destination = self.origin
        self.set_coordinates(origin, destination)

        self.params = {
            'coordinates': self.coordinates,
            'profile': 'foot-walking'
        }
        if kwargs:
            self.add_params(**kwargs)

        api_request = requests.get(self.url, params=self.params)
        api_response = api_request.text

        return api_response