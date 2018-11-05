from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('busstops', views.BusStopViewSet)
router.register('courses', views.CourseViewSet, 'courses_router')
router.register('carrierstops', views.CarrierStopViewSet)

urlpatterns = [
    path('', views.search, name='search_engine'),
    path('restapi/', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

