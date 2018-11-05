
from bushelper.models import *
import numpy as np


def replace_types_gen(types):
    for t in types:
        t = str(t).lower()
        if 'powszed' in t:
            yield 'D'
        elif 'sobot' in t:
            yield 'E'
        elif 'niedz' in t or 'świąt' in t:
            yield '7'
        elif 'nocn' in t:
            yield 'DE7'
        else:
            yield 'E'


def filtered_by_dest(courses, origin, destination, direction):
    """Generator that filter courses. Yield only courses which goes to/through destination bus stop."""
    carrier_stops = CarrierStop.objects.filter(direction__direction=direction)
    for cs in carrier_stops:
        if cs.line:
            filtered_courses = courses.filter(carrier=cs.carrier).filter(line=cs.line)
        else:
            filtered_courses = courses.filter(carrier=cs.carrier)
        if filtered_courses:
            order_list = CarrierStopOrder.objects.filter(carrier_stop=cs).values_list('order', flat=True)
            origin_order = CarrierStopOrder.objects.filter(carrier_stop=cs).filter(bus_stop=origin).values_list(
                'order',
                flat=True).first()
            destination_order = CarrierStopOrder.objects.filter(carrier_stop=cs).filter(
                bus_stop=destination).values_list(
                'order',
                flat=True).first()
            order_np = np.array(order_list)
            if origin_order is not None or destination_order is not None:
                order_np = order_np[order_np > origin_order]
                if destination_order in order_np:
                    yield filtered_courses

