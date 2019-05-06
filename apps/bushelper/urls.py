from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views

app_name = 'bushelper'

router = SimpleRouter()

router.register('bus_stops', views.BusStopViewSet, 'bus_stops')
router.register('courses', views.BusStopViewSet, 'courses')

urlpatterns = [
    path('', views.SearchEngineView.as_view(), name='search_engine'),
    path('search/', views.DirectionsView.as_view(), name='directions'),
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
