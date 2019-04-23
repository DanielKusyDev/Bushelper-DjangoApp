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


def filtered_by_dest(courses, origin, destination, direction):
    """Performs BFS to filter courses connected with origin and destination"""
    queue = [(origin, carrier.pk, carrier.line) for carrier in Carrier.objects.all()]
    valid_courses = []
    while queue:
        current_source_and_node = queue.pop()
        # for neighbour in current_source_and_node[1].neighbours.filter(direction__name=direction):

    connected_bus_stops = BusStop.objects.filter(direction__name=direction)
    for cs in connected_bus_stops:
        if cs.line:
            filtered_courses = courses.filter(carrier=cs.carrier).filter(line=cs.line)
        else:
            filtered_courses = courses.filter(carrier=cs.carrier)
        if filtered_courses:
            order_list = CarrierStopOrder.objects.filter(carrier_stop=cs).values_list('order', flat=True)
            origin_order = CarrierStopOrder.objects.filter(carrier_stop=cs).filter(bus_stop__mpk_street__exact=origin).values_list(
                'order',
                flat=True).first()
            destination_order = CarrierStopOrder.objects.filter(carrier_stop=cs).filter(
                bus_stop=destination).values_list(
                'order',
                flat=True).first()
            order_np = np.array(order_list)
            if origin_order is not None or destination_order is not None:
                order_np = order_np[order_np > origin_order]
                if destination_order in order_np:
                    yield filtered_courses


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