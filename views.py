from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.bushelper.forms import SearchForm
from apps.bushelper.models import BusStop, Course, CarrierStop
from apps.bushelper.serializers import UserSerializer, CourseSerializer, BusStopSerializer, CarrierStopSerializer
from apps.bushelper.custom.managers import *


class SearchEngineView(TemplateView):
    template_name = 'bushelper/search_engine.html'

    def get(self, request, **kwargs):
        if not request.GET:
            form = SearchForm
            context = {
                'form': form
            }
            return render(request, self.template_name, context)


def search(request):
    direction = request.GET.get('direction')
    destination = BusStop.objects.get(mpk_street=request.GET.get('destination'), direction__direction=direction)
    custom_location = CustomLocation()
    if request.GET.get('coordinates'):
        coordinates = request.GET.get('coordinates')
        closest_stop = get_closest_valid_stop(coordinates, destination)
        try:
            courses = get_valid_courses_between_stops(closest_stop, destination, direction)
            custom_location.context['courses'] = courses
            paginator = Paginator(courses, 5)
            page = request.GET.get('page')
            custom_location.context['courses'] = paginator.get_page(page)
            custom_location.set_essentials(origin=coordinates, destination=closest_stop, direction=direction)
            custom_location.context['walking_directions_api'] = custom_location.get_directions('foot-walking')
            custom_location.set_essentials(origin=closest_stop, destination=destination, direction=direction)
            custom_location.context['directions_api'] = custom_location.get_directions('driving-car')
            template_name = 'bushelper/regular_directions.html'
        except NoCoursesAvailableError:
            custom_location.set_essentials(origin=coordinates, destination=destination, direction=direction)
            custom_location.context['directions_api'] = custom_location.get_directions('foot-walking')
            template_name = 'bushelper/walking_directions.html'
    else:
        origin = BusStop.objects.get(mpk_street=request.GET.get('origin'), direction__direction=direction)
        try:
            courses = get_valid_courses_between_stops(origin, destination, direction)
            custom_location.context['courses'] = courses
            paginator = Paginator(courses, 5)
            page = request.GET.get('page')
            custom_location.context['courses'] = paginator.get_page(page)
            custom_location.set_essentials(origin=origin, destination=destination, direction=direction)
            custom_location.context['directions_api'] = custom_location.get_directions('driving-car')
            template_name = 'bushelper/regular_directions.html'
        except NoCoursesAvailableError:
            raise Http404
    context = custom_location.context
    return render(request, template_name, context)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.all()
        id = self.request.query_params.get('id')
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
