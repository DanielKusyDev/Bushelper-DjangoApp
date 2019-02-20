from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('busstops', views.BusStopViewSet)
router.register('courses', views.CourseViewSet, 'courses_router')
router.register('carrierstops', views.CarrierStopViewSet)

urlpatterns = [
    path('', views.SearchEngineView.as_view(), name='search_engine_view'),
    path('directions/', views.DirectionsView.as_view(), name='directions_view'),
    path('restapi/', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

