from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.bushelper.urls'), name='bushelper'),
    path('', include('apps.users.urls'), name='users'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler400 = 'dkusy.views.bad_request_400'
handler404 = 'personalwebsite.views.not_found_404'
handler500 = 'dkusy.views.server_error_500'
