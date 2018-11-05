from django.contrib import admin

from .models import *


admin.site.register(Departure)
admin.site.register(BusStop)
admin.site.register(Carrier)
admin.site.register(Course)
admin.site.register(CarrierStop)
admin.site.register(CarrierStopOrder)