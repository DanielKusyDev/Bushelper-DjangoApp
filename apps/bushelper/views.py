from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from apps.bushelper.forms import SearchForm
from apps.bushelper.custom.managers import *
from apps.bushelper.serializers import BusStopSerializer

TEMPLATE_PREFIX = 'bushelper/templates/bushelper/'


def get_template_name(path):
    return TEMPLATE_PREFIX+path


class SearchEngineView(TemplateView):
    template_name = get_template_name('search_engine.html')

    def get(self, request, **kwargs):
        form = SearchForm
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SearchForm(request.POST)
        if form.is_valid():
            return self.search(request, form)
        return render(request, self.template_name, {'form': form})

    def search(self, request, form):
        data = form.cleaned_data
        try:
            destination = BusStop.objects.get(mpk_street=data['destination'], direction__name=data['direction'])
        except ObjectDoesNotExist:
            raise Http404
        custom_location = CustomLocation()
        if data.get('coordinates'):
            closest_stop = get_closest_valid_stop(data['coordinates'], destination)
            try:
                courses = get_valid_courses_between_stops(closest_stop, destination, data['direction'])
                custom_location.context['courses'] = courses
                paginator = Paginator(courses, 5)
                page = request.POST.get('page')
                custom_location.context['courses'] = paginator.get_page(page)
                custom_location.set_essentials(origin=data['coordinates'], destination=closest_stop, direction=data['direction'])
                custom_location.context['walking_directions_api'] = custom_location.get_directions('foot-walking')
                custom_location.set_essentials(origin=closest_stop, destination=destination, direction=data['direction'])
                custom_location.context['directions_api'] = custom_location.get_directions('driving-car')
                template_name = get_template_name('regular_directions.html')
            except NoCoursesAvailableError:
                custom_location.set_essentials(origin=data['coordinates'], destination=destination, direction=data['direction'])
                custom_location.context['directions_api'] = custom_location.get_directions('foot-walking')
                template_name = get_template_name('walking_directions.html')
        else:
            origin = BusStop.objects.get(mpk_street=data['origin'], direction__name=data['direction'])
            try:
                courses = get_valid_courses_between_stops(origin, destination, data['direction'])
                custom_location.context['courses'] = courses
                paginator = Paginator(courses, 5)
                page = request.POST.get('page')
                custom_location.context['courses'] = paginator.get_page(page)
                custom_location.set_essentials(origin=origin, destination=destination, direction=data['direction'])
                custom_location.context['directions_api'] = custom_location.get_directions('driving-car')
                template_name = get_template_name('regular_directions.html')
            except NoCoursesAvailableError:
                raise Http404
        context = custom_location.context
        return render(request, template_name, context)


class BusStopViewSet(viewsets.ModelViewSet):
    queryset = BusStop.objects.all().order_by('pk')
    serializer_class = BusStopSerializer
    paginator = None

