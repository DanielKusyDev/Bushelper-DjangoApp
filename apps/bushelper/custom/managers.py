import math
from datetime import datetime

from django.db.models import Q

from .openroute import *
from .utils import *
from apps.bushelper.models import *


def get_closest_valid_stop(coordinates, destination):
    coordinates = parse_coordinates(coordinates)
    participating_lines = CarrierStopOrder.objects.filter(bus_stop__mpk_street__exact=destination).values_list(
        'carrier_stop', flat=True)
    connected_stops = CarrierStopOrder.objects.filter(carrier_stop__in=participating_lines).values_list(
        'bus_stop', flat=True)
    closest_stop = BusStop.objects.get(id=connected_stops[0])
    closest_stop_coords = [closest_stop.latitude, closest_stop.longtitude]
    min_distance = math.sqrt(
        math.pow((closest_stop_coords[0] - coordinates[1]), 2) +
        math.pow((closest_stop_coords[1] - coordinates[0]), 2))

    for stop_pk in connected_stops:
        bus_stop = BusStop.objects.filter(pk=stop_pk).first()
        bus_stop_coords = [bus_stop.latitude, bus_stop.longtitude]
        distance = math.sqrt(
            math.pow((bus_stop_coords[0] - coordinates[1]), 2) +
            math.pow((bus_stop_coords[1] - coordinates[0]), 2))

        if distance < min_distance:
            min_distance = distance
            closest_stop = bus_stop

    return closest_stop


def get_valid_courses_between_stops(origin, destination, direction):
    curr_day = datetime.now().weekday()
    if 0 <= curr_day <= 5:
        unfiltered_courses = Course.objects.filter(direction__name=direction,
                                                   bus_stop__mpk_street__exact=origin).filter(
            Q(course_type__contains='E') |
            Q(course_type__contains='D')
            ).order_by('departure__hour')
    else:
        if curr_day == 5:
            searched_type = 'E'
        elif curr_day == 6:
            searched_type = '7'
        else:
            raise WeekdaysValueError
        unfiltered_courses = Course.objects.filter(direction__name=direction,
                                                   bus_stop__mpk_street__exact=origin,
                                                   course_type__contains=searched_type).order_by('departure__hour')

    courses = unfiltered_courses.filter(
        Q(departure__hour__gt=datetime.now().hour) |
        Q(departure__hour=datetime.now().hour,
          departure__minute__gte=datetime.now().minute))

    course_lists = [result for result in filtered_by_dest(courses, origin, destination, direction)]
    if not course_lists:
        raise NoCoursesAvailableError
    else:
        courses = [course for course_list in course_lists for course in course_list]
        courses.sort(key=lambda l: str(l.departure))

    return courses


class CustomLocation(object):
    """Klasa definiująca widok, wywoływany gdy użytkownik nie wybierze przystanku odjazdu, tylko poda swoją obecną
    lokalizację. Instancja klasy parsuje obecną lokalizację pobraną z przeglądarki na typ odpowiedni dla
    OpenrouteDirections API, oblicza dystans do najbliższego połączonego z miejscem docelowym przystanku, wysyła żądanie
    API o pieszą drogą do przystanku i zwraca obliczone wartości oraz Geojson z wynikiem żądania."""

    def __init__(self):
        self.context = {}

    def set_essentials(self, origin, destination, direction):
        origin_c = parse_coordinates(origin)
        destination_c = parse_coordinates(destination)
        if isinstance(origin, str):
            self.context['origin'] = Point(origin_c[0], origin_c[1], 'START')
        elif isinstance(origin, BusStop):
            self.context['origin'] = Point(origin_c[0], origin_c[1], origin.__str__())
        self.context['destination'] = Point(destination_c[0], destination_c[1], destination.__str__())
        self.context['direction'] = direction

    def get_directions(self, profile):
        """Profiles: foot-walking, car-driving """
        directions_api = OpenrouteDirections(self.context['origin'], self.context['destination'])
        directions_api = directions_api.get_api_data(profile)
        return directions_api


class DefinedLocalization(object):
    """Klasa definiująca widok, wywoływany gdy użytkownik wybierze przystanek odjazdu 'na sztywno'. Wyszukuje dostępne
        kursy, sortuje je, tworzy paginator i ustawia OpenRouteDirections API dla skryptu Leaflet. Jeżeli kursów nie ma, to
        wysyła żądanie do API o drogę pieszą."""

    pass