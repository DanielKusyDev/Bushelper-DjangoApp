import math
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from bushelper.forms import SearchForm
from bushelper.models import BusStop, CarrierStopOrder, Course, CarrierStop
from bushelper.serializers import UserSerializer, CourseSerializer, BusStopSerializer, CarrierStopSerializer
from bushelper.utils import OpenrouteDirections, WeekdaysValueError, filtered_by_dest, NoCoursesAvailableError


class CustomLocalization(object):
    """Klasa definiująca widok, wywoływany gdy użytkownik nie wybierze przystanku odjazdu, tylko poda swoją obecną
    lokalizację. Instancja klasy parsuje obecną lokalizację pobraną z przeglądarki na typ odpowiedni dla
    OpenrouteDirections API, oblicza dystans do najbliższego połączonego z miejscem docelowym przystanku, wysyła żądanie
    API o pieszą drogą do przystanku i zwraca obliczone wartości oraz Geojson z wynikiem żądania."""

    def __init__(self):
        self.context = {}

    def __call__(self, GET):

        current_location = GET['coordinates']
        current_location = self.set_location(current_location)

        direction = GET['direction']
        destination = BusStop.objects.filter(mpk_street=GET['destination']).filter(
            direction__direction=direction).first()
        self.context['destination'] = destination
        self.set_origin(destination, current_location)
        origin = self.context['origin']
        directions_api = self.get_directions_api(current_location, origin)

        class Point(object):
            def __init__(self, longtitude, latitude, name):
                self.longtitude = longtitude
                self.latitude = latitude
                self.name = name

            def __str__(self):
                return self.name

        self.context['destination'] = Point(origin.longtitude, origin.latitude, origin.mpk_street)
        self.context['origin'] = Point(current_location[1], current_location[0], 'START')
        self.set_travel_duration(directions_api)
        self.context['directions_api'] = directions_api
        return self.context

    def __getitem__(self, item):
        return self.context[item]

    def set_location(self, current_location):
        current_location = current_location.split(',')
        current_location = [float(current_location[0]), float(current_location[1])]
        self.context['current_location'] = current_location
        return current_location

    def set_origin(self, destination, current_location):
        participating_lines = CarrierStopOrder.objects.filter(bus_stop=destination).values_list(
            'carrier_stop', flat=True)
        connected_stops = CarrierStopOrder.objects.filter(carrier_stop__in=participating_lines).values_list(
            'bus_stop', flat=True)
        closest_stop = BusStop.objects.filter(id=connected_stops[0]).first()
        closest_stop_coords = [closest_stop.latitude, closest_stop.longtitude]
        min_distance = math.sqrt(
            math.pow((closest_stop_coords[0] - current_location[0]), 2) +
            math.pow((closest_stop_coords[1] - current_location[1]), 2))

        for stop_pk in connected_stops:
            bus_stop = BusStop.objects.filter(pk=stop_pk).first()
            bus_stop_coords = [bus_stop.latitude, bus_stop.longtitude]
            distance = math.sqrt(
                math.pow((bus_stop_coords[0] - current_location[0]), 2) +
                math.pow((bus_stop_coords[1] - current_location[1]), 2))

            if distance < min_distance:
                min_distance = distance
                closest_stop = bus_stop

        self.context['origin'] = closest_stop

    def get_directions_api(self, current_location, origin):
        directions_api = OpenrouteDirections(current_location, origin)
        directions_api = directions_api.get_api_data('foot-walking')
        return directions_api

    def set_travel_duration(self, directions_api):
        directions = json.loads(directions_api)
        travel_duration = directions['features'][0]['properties']['summary'][0]['duration']
        self.context['travel_duration'] = int(travel_duration / 60 + 1)


class DefinedLocalization(object):
    """Klasa definiująca widok, wywoływany gdy użytkownik wybierze przystanek odjazdu 'na sztywno'. Wyszukuje dostępne
        kursy, sortuje je, tworzy paginator i ustawia OpenRouteDirections API dla skryptu Leaflet. Jeżeli kursów nie ma, to
        wysyła żądanie do API o drogę pieszą."""

    template_name = 'bushelper/regular_directions.html'

    def __init__(self):
        self.context = {}

    def __call__(self, GET, origin=None):
        self.context['destination'] = BusStop.objects.filter(mpk_street=GET['destination']).filter(
            direction__direction=GET['direction']).first()
        if origin is None:
            self.context['origin'] = BusStop.objects.filter(mpk_street=GET['origin']).filter(
                direction__direction=GET['direction']).first()
        elif origin == GET['destination']:
            raise Http404
        else:
            self.context['origin'] = origin
        self.context['direction'] = GET['direction']

        try:
            courses = self.filter_courses()
            courses = self.sort_and_set_courses(courses)
            if 'page' in GET:
                paginator = Paginator(courses, 5)
                paginator.get_page(GET['page'])
                # self.set_absolute_url()
            directions_api = self.set_directions_api()
        except NoCoursesAvailableError:
            directions_api = OpenrouteDirections(self.context['origin'], self.context['destination'])
            directions_api = directions_api.get_api_data('foot-walking')
            self.template_name = None

        self.context['directions_api'] = directions_api
        return self.context

    def filter_courses(self):
        direction = self.context['direction']
        origin = self.context['origin']
        curr_day = datetime.now().weekday()
        if 0 <= curr_day <= 5:
            unfiltered_courses = Course.objects.filter(direction__direction=direction,
                                                       bus_stop=origin).filter(Q(course_type__contains='E') |
                                                                               Q(course_type__contains='D')
                                                                               ).order_by('departure__hour')
        else:
            if curr_day == 5:
                searched_type = 'E'
            elif curr_day == 6:
                searched_type = '7'
            else:
                raise WeekdaysValueError
            unfiltered_courses = Course.objects.filter(direction__direction=direction,
                                                       bus_stop=origin,
                                                       course_type__contains=searched_type).order_by('departure__hour')
        courses = unfiltered_courses.filter(
            Q(departure__hour__hour__gt=datetime.now().hour) |
            Q(departure__hour__hour=datetime.now().hour,
              departure__hour__minute__gte=datetime.now().minute))
        return courses

    def sort_and_set_courses(self, courses):
        origin = self.context['origin']
        direction = self.context['direction']
        destination = self.context['destination']
        course_lists = [result for result in filtered_by_dest(courses, origin,
                                                              destination, direction)]

        if not course_lists:
            raise NoCoursesAvailableError
        else:
            courses = [course for course_list in course_lists for course in course_list]
            courses.sort(key=lambda l: str(l.departure))
        return courses

    def set_directions_api(self):
        origin = self.context['origin']
        destination = self.context['destination']
        directions_api = OpenrouteDirections(origin, destination)
        directions_api = directions_api.get_api_data('driving-car')
        return directions_api


class SearchEngineView(TemplateView):
    template_name = 'bushelper/search_engine.html'

    def get(self, request, **kwargs):
        if not request.GET:
            form = SearchForm
            context = {
                'form': form
            }
            return render(request, self.template_name, context)


class DirectionsView(TemplateView):
    template_name = 'bushelper/walking_directions.html'

    def get(self, request, **kwargs):
        if request.GET.get('coordinates'):
            custom_localization = CustomLocalization()
            c_context = custom_localization(request.GET)
            if c_context['origin'] == c_context['destination']:
                return render(request, self.template_name, c_context)
            defined_localization = DefinedLocalization()
            d_context = defined_localization(request.GET, c_context['origin'])
            if defined_localization.template_name is None:
                return render(request, self.template_name, d_context)

            self.template_name = defined_localization.template_name
            defined_localization.context['walking_directions_api'] = c_context['destinations_api']
            defined_localization.context['travel_duration'] = c_context['travel_duration']
            return render(request, self.template_name, d_context)
        else:
            defined_localization = DefinedLocalization()
            context = defined_localization(request.GET)
            if defined_localization.template_name is None:
                return render(request, self.template_name, context)
            self.template_name = defined_localization.template_name
            return render(request, self.template_name, context)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.all()
        id = self.request.query_params.get('id', )
        if id is not None:
            queryset = queryset.filter(id=id)
        return queryset


class BusStopViewSet(viewsets.ModelViewSet):
    queryset = BusStop.objects.all().order_by('pk')
    serializer_class = BusStopSerializer
    paginator = None


class CarrierStopViewSet(viewsets.ModelViewSet):
    queryset = CarrierStop.objects.all()
    serializer_class = CarrierStopSerializer
    paginator = None


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'busstops': reverse('busstops-list', request=request, format=format),
        'courses': reverse('courses-list', request=request, format=format),
        'carrierstop': reverse('carrierstop-list', request=request, format=format)
    })
