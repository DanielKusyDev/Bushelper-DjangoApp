from django.db import models


class Direction(models.Model):
    direction = models.CharField(max_length=3)

    def __str__(self):
        return self.direction


class BusStop(models.Model):
    mpk_street = models.CharField(max_length=255, default='')
    fremiks_alias = models.CharField(max_length=255, null=True, blank=True)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='busstop_direction_fk')
    latitude = models.FloatField()
    longtitude = models.FloatField()
    neighbour = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '%s' % self.mpk_street

    class Meta:
        ordering = ['mpk_street']


class Carrier(models.Model):
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=127, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Line(models.Model):
    name = models.CharField(max_length=8)
    url = models.URLField()

    def __str__(self):
        return self.name


class Course(models.Model):
    departure = models.TimeField(null=False)
    course_type = models.CharField(max_length=7, unique=False, null=False)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='course_line_fk', null=True, blank=True)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='course_direction_fk')
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='course_carrier_fk')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='course_stop_fk')

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return "%s %s" % (self.departure, self.carrier)


class CarrierStop(models.Model):
    bus_stop = models.ManyToManyField(BusStop, through='CarrierStopOrder', related_name='carrierstop_busstop_fk')
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='carrierstop_line_fk', null=True, blank=True)
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='carrierstop_carrier_fk')
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='carrierstop_direction_fk')

    def __str__(self):
        return "%s %s %s" % (self.carrier, (self.line if self.line else ''), self.direction)


class CarrierStopOrder(models.Model):
    carrier_stop = models.ForeignKey(CarrierStop, on_delete=models.CASCADE, related_name='carrierstoporder_carrierstop_fk')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='carrierstoporder_busstop_fk')
    order = models.PositiveIntegerField()

    def __str__(self):
        return "%d %s %s" % (self.order, self.carrier_stop, self.bus_stop)
