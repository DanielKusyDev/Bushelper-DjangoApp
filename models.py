from django.db import models as m


class Direction(m.Model):
    direction = m.CharField(max_length=3)

    def __str__(self):
        return self.direction


class BusStop(m.Model):
    mpk_street = m.CharField(max_length=255, default='')
    fremiks_alias = m.CharField(max_length=255, null=True, blank=True)
    direction = m.ForeignKey(Direction, on_delete=m.CASCADE, related_name='busstop_direction_fk')
    latitude = m.FloatField()
    longtitude = m.FloatField()

    def __str__(self):
        return '%s' % self.mpk_street

    class Meta:
        ordering = ['mpk_street']


class Carrier(m.Model):
    name = m.CharField(max_length=255)
    number = m.IntegerField(null=True, blank=True)
    website = m.CharField(max_length=127, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Line(m.Model):
    name = m.CharField(max_length=8)
    url = m.URLField()

    def __str__(self):
        return self.name


class Course(m.Model):
    departure = m.TimeField(null=False)
    course_type = m.CharField(max_length=7, unique=False, null=False)
    line = m.ForeignKey(Line, on_delete=m.CASCADE, related_name='course_line_fk', null=True, blank=True)
    direction = m.ForeignKey(Direction, on_delete=m.CASCADE, related_name='course_direction_fk')
    carrier = m.ForeignKey(Carrier, on_delete=m.CASCADE, related_name='course_carrier_fk')
    bus_stop = m.ForeignKey(BusStop, on_delete=m.CASCADE, related_name='course_stop_fk')

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return "%s %s" % (self.departure, self.carrier)


class CarrierStop(m.Model):
    bus_stop = m.ManyToManyField(BusStop, through='CarrierStopOrder', related_name='carrierstop_busstop_fk')
    line = m.ForeignKey(Line, on_delete=m.CASCADE, related_name='carrierstop_line_fk', null=True, blank=True)
    carrier = m.ForeignKey(Carrier, on_delete=m.CASCADE, related_name='carrierstop_carrier_fk')
    direction = m.ForeignKey(Direction, on_delete=m.CASCADE, related_name='carrierstop_direction_fk')

    def __str__(self):
        return "%s %s %s" % (self.carrier, (self.line if self.line else ''), self.direction)


class CarrierStopOrder(m.Model):
    carrier_stop = m.ForeignKey(CarrierStop, on_delete=m.CASCADE, related_name='carrierstoporder_carrierstop_fk')
    bus_stop = m.ForeignKey(BusStop, on_delete=m.CASCADE, related_name='carrierstoporder_busstop_fk')
    order = m.PositiveIntegerField()

    def __str__(self):
        return "%d %s %s" % (self.order, self.carrier_stop, self.bus_stop)
