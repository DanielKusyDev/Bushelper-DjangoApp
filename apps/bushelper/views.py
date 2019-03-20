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
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            return self.search(request, search_form)

    def search(self, request, form):
        data = form.cleaned_data
        try:
            destination = BusStop.objects.get(mpk_street=data['destination'], direction__direction=data['direction'])
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
            origin = BusStop.objects.get(mpk_street=data['origin'], direction__direction=data['direction'])
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

# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# class CourseViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = CourseSerializer
#
#     def get_queryset(self):
#         queryset = Course.objects.all()
#         id = self.request.query_params.get('id')
#         if id is not None:
#             queryset = queryset.filter(id=id)
#         return queryset
#
#
# class BusStopViewSet(viewsets.ModelViewSet):
#     queryset = BusStop.objects.all().order_by('pk')
#     serializer_class = BusStopSerializer
#     paginator = None
#
#
# class CarrierStopViewSet(viewsets.ModelViewSet):
#     queryset = CarrierStop.objects.all()
#     serializer_class = CarrierStopSerializer
#     paginator = None
#

# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'busstops': reverse('busstops-list', request=request, format=format),
#         'courses': reverse('courses-list', request=request, format=format),
#         'carrierstop': reverse('carrierstop-list', request=request, format=format)
#     })
