import json
import math
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from bushelper.permissions import IsOwnerOrReadOnly
from bushelper.utils import *
from .forms import SearchForm
from .serializers import *


class LocalizationView(object):
    """Klasa bazowa dla widoków używanych przy wyborze lokalizacji z góry oraz poprzez pobranie lokalizacji."""

    def __init__(self, request):
        self.request = request
        self.direction = request.GET.get('direction')
        self.destination = BusStop.objects.filter(mpk_street=self.request.GET.get('destination')).filter(
            direction__direction=self.direction).first()
        self.context = {
            'destination': self.destination
        }
        self.courses = None
        self.template_name = None

    def as_view(self):
        return render(self.request, self.template_name, self.context)


class PredefinedLocalizationView(LocalizationView):
    """Klasa definiująca widok, wywoływany gdy użytkownik wybierze przystanek odjazdu 'na sztywno'. Wyszukuje dostępne
    kursy, sortuje je, tworzy paginator i ustawia OpenRouteDirections API dla skryptu Leaflet. Jeżeli kursów nie ma, to
    wysyła żądanie do API o drogę pieszą."""

    def __init__(self, request, origin=None):
        super().__init__(request)

        if origin is not None:
            self.origin = origin
        else:
            self.origin = BusStop.objects.filter(mpk_street=request.GET.get('origin')).filter(
                direction__direction=self.direction).first()

        self.context['origin'] = self.origin

    def filter_courses(self):
        curr_day = datetime.now().weekday()
        if 0 <= curr_day <= 5:
            unfiltered_courses = Course.objects.filter(direction__direction=self.direction,
                                                       bus_stop=self.origin).filter(Q(course_type__contains='E') |
                                                                                    Q(course_type__contains='D')
                                                                                    ).order_by('departure__hour')
        else:
            if curr_day == 5:
                searched_type = 'E'
            elif curr_day == 6:
                searched_type = '7'
            else:
                raise WeekdaysValueError
            unfiltered_courses = Course.objects.filter(direction__direction=self.direction,
                                                       bus_stop=self.origin,
                                                       course_type__contains=searched_type).order_by('departure__hour')
        self.courses = unfiltered_courses.filter(
            Q(departure__hour__hour__gt=datetime.now().hour) |
            Q(departure__hour__hour=datetime.now().hour,
              departure__hour__minute__gte=datetime.now().minute))


    def handle_no_available_courses_error(self):
        directions_api = OpenrouteDirections(self.origin, self.destination)
        directions_api = directions_api.get_api_data('foot-walking')
        self.context['directions_api'] = directions_api
        self.template_name = 'bushelper/walking_directions.html'

    def sort_and_set_courses(self):
        course_lists = [result for result in filtered_by_dest(self.courses, self.origin,
                                                              self.destination, self.direction)]

        if not course_lists:
            raise NoCoursesAvailableError
        else:
            self.courses = [course for course_list in course_lists for course in course_list]
            self.courses.sort(key=lambda l: str(l.departure))

    def create_paginator(self):
        paginator = Paginator(self.courses, 5)
        page = self.request.GET.get('page')
        courses_per_page = paginator.get_page(page)
        self.context['courses'] = courses_per_page

    def set_absolute_url(self):
        path = self.request.path + '?'
        for param in self.request.GET:
            if param != 'page':
                path += param + '='
                path += self.request.GET[param]
                path += '&'
        path = path.strip('&')
        path = path.replace(' ', '+')
        self.context['path'] = path

    def set_directions_api(self):
        directions_api = OpenrouteDirections(self.origin, self.destination)
        directions_api = directions_api.get_api_data('driving-car')
        self.context['directions_api'] = directions_api
        self.template_name = 'bushelper/regular_directions.html'

    def set_context_data(self):

        if self.origin == self.destination:
            raise Http404

        try:
            self.filter_courses()
            self.sort_and_set_courses()
            self.create_paginator()
            self.set_absolute_url()
            self.set_directions_api()
        except NoCoursesAvailableError:
            self.handle_no_available_courses_error()

    def add_additional_directions(self, directions):
        self.context['walking_directions_api'] = directions


class CustomLocalizationView(LocalizationView):
    """Klasa definiująca widok, wywoływany gdy użytkownik nie wybierze przystanku odjazdu, tylko poda swoją obecną
    lokalizację. Instancja klasy parsuje obecną lokalizację pobraną z przeglądarki na typ odpowiedni dla
    OpenrouteDirections API, oblicza dystans do najbliższego połączonego z miejscem docelowym przystanku, wysyła żądanie
    API o pieszą drogą do przystanku i zwraca obliczone wartości oraz Geojson z wynikiem żądania."""

    def __init__(self, request):
        super().__init__(request)
        self.current_location = request.GET.get('coordinates')
        self.origin = None
        self.directions_api = None
        self.travel_duration = None

    def set_location(self):
        self.current_location = self.current_location.split(',')
        self.current_location = [float(self.current_location[0]), float(self.current_location[1])]
        self.context['current_location'] = self.current_location

    def calculate_and_set_origin(self):
        participating_lines = CarrierStopOrder.objects.filter(bus_stop=self.destination).values_list(
            'carrier_stop', flat=True)
        connected_stops = CarrierStopOrder.objects.filter(carrier_stop__in=participating_lines).values_list(
            'bus_stop', flat=True)
        closest_stop = BusStop.objects.filter(id=connected_stops[0]).first()
        closest_stop_coords = [closest_stop.latitude, closest_stop.longtitude]
        min_distance = math.sqrt(
            math.pow((closest_stop_coords[0] - self.current_location[0]), 2) +
            math.pow((closest_stop_coords[1] - self.current_location[1]), 2))

        for stop_pk in connected_stops:
            bus_stop = BusStop.objects.filter(pk=stop_pk).first()
            bus_stop_coords = [bus_stop.latitude, bus_stop.longtitude]
            distance = math.sqrt(
                math.pow((bus_stop_coords[0] - self.current_location[0]), 2) +
                math.pow((bus_stop_coords[1] - self.current_location[1]), 2))

            if distance < min_distance:
                min_distance = distance
                closest_stop = bus_stop
                self.origin = closest_stop
        self.context['origin'] = self.origin

    def set_directions_api(self):
        directions_api = OpenrouteDirections(self.current_location, self.origin)
        self.directions_api = directions_api.get_api_data('foot-walking')
        self.context['directions_api'] = self.directions_api

        class Point(object):
            def __init__(self, longtitude, latitude, name):
                self.longtitude = longtitude
                self.latitude = latitude
                self.name = name

            def __str__(self):
                return self.name
        self.context['destination'] = Point(self.origin.longtitude, self.origin.latitude, self.origin.mpk_street)
        self.context['origin'] = Point(self.current_location[1], self.current_location[0], 'START')
        self.set_travel_duration(self.directions_api)

    def set_travel_duration(self, directions):
        directions = json.loads(directions)
        travel_duration = directions['features'][0]['properties']['summary'][0]['duration']
        self.travel_duration = int(travel_duration/60 + 1)
        self.context['x'] = self.travel_duration

    def get_travel_duration(self):
        return self.travel_duration

    def set_template(self):
        self.template_name = 'bushelper/walking_directions.html'

    def set_context_data(self):
        self.set_location()
        self.calculate_and_set_origin()
        try:
            self.set_directions_api()
        except Http404:
            pass

    def is_destination_close(self):
        return self.origin == self.destination

    def get_endpoints(self):
        return self.origin, self.directions_api


def search_engine_view(request):
    form = SearchForm()
    context = {
        'form': form
    }
    return render(request, 'bushelper/search_engine.html', context)


def search(request):

    if request.GET:
        if request.GET.get('coordinates'):
            custom_localization_view = CustomLocalizationView(request)
            custom_localization_view.set_context_data()
            if custom_localization_view.is_destination_close():
                custom_localization_view.set_template()
                return custom_localization_view.as_view()

            origin, custom_localization_directions_api = custom_localization_view.get_endpoints()

            predefined_localization_view = PredefinedLocalizationView(request, origin)
            predefined_localization_view.set_context_data()
            predefined_localization_view.add_additional_directions(custom_localization_directions_api)
            predefined_localization_view.context['travel_duration'] = custom_localization_view.get_travel_duration()
            return predefined_localization_view.as_view()

        elif request.GET.get('origin'):
            predefined_localization_view = PredefinedLocalizationView(request)
            predefined_localization_view.set_context_data()
            return predefined_localization_view.as_view()
    else:
        return search_engine_view(request)


def current_location_result(request):
    return render(request, 'temp.html')


def schedule(request):
    return render(request, 'bushelper/schedule/schedule.html', {'html_names': 'Będzie kiedyś'})


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
        id = self.request.query_params.get('id', None)
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    return Response({
        'busstops': reverse('busstops-list', request=request, format=format),
        'courses': reverse('courses-list', request=request, format=format),
        'carrierstop': reverse('carrierstop-list', request=request, format=format)
    })
