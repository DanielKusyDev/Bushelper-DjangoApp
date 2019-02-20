from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from bushelper.custom.managers import *
from bushelper.forms import SearchForm
from bushelper.models import BusStop, Course, CarrierStop
from bushelper.serializers import UserSerializer, CourseSerializer, BusStopSerializer, CarrierStopSerializer


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
