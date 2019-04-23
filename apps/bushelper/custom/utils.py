import numpy as np

from apps.bushelper.models import CarrierStop, CarrierStopOrder, BusStop, Carrier


def replace_types_gen(types):
    for t in types:
        t = str(t).lower()
        if 'powszed' in t:
            yield 'D'
        elif 'sobot' in t:
            yield 'E'
        elif 'niedz' in t or 'świąt' in t:
            yield '7'
        elif 'nocn' in t:
            yield 'DE7'
        else:
            yield 'E'


class WeekdaysValueError(ValueError):
    """Raised when weekdays not in (0,6)"""
    pass


class NoCoursesAvailableError(ValueError):
    """Raised when there is no available courses"""
    pass


class SameBusStopError(Exception):
    pass


def get_valid_courses_by_bfs(courses, origin, destination, direction):
    """Performs BFS to filter courses connected with origin and destination"""
    lines = set([course.line for course in courses])
    for line in lines:
        pass

    queue = [origin]
    visited = {bus_stop.pk: False for bus_stop in BusStop.objects.all()}
    while queue:
        curr_node = queue.pop(0)
        for neighbour in curr_node.neighbours.all():
            if not visited[neighbour.pk]:
                visited[neighbour.pk] = True




class Point(object):
    def __init__(self, longtitude, latitude, name):
        self.longtitude = longtitude
        self.latitude = latitude
        self.name = name

    def __str__(self):
        return self.name


def parse_coordinates(coordinates):
    if isinstance(coordinates, str):
        coordinates = coordinates.split(',')
        coordinates[0], coordinates[1] = coordinates[1], coordinates[0]
        coordinates = (float(coordinates[0]), float(coordinates[1]))
    elif isinstance(coordinates, BusStop):
        coordinates = (float(coordinates.longitude), float(coordinates.latitude))
    return coordinates