from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('apps.bushelper.urls'), name='bushelper'),
    # path('', include('apps.users.urls'), name='users'),
]

if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# handler400 = 'dkusy.views.bad_request_400'
# handler404 = 'dkusy.views.not_found_404'
# handler500 = 'dkusy.views.server_error_500'
