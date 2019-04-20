from django.db import models


class Direction(models.Model):
    name = models.CharField(max_length=3)

    def __str__(self):
        return self.direction


class BusStop(models.Model):
    mpk_street = models.CharField(max_length=255, default='')
    fremiks_alias = models.CharField(max_length=255, null=True, blank=True)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    neighbours = models.ManyToManyField(to='self')

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
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True, blank=True, related_name='course_line')
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='course_direction')
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='course_carrier')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='course_bus_stop')

    def __str__(self):
        return "%s %s" % (self.departure, self.carrier)


class CarrierStop(models.Model):
    bus_stop = models.ManyToManyField(BusStop, through='CarrierStopOrder')
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True, blank=True)
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s %s" % (self.carrier, (self.line if self.line else ''), self.direction)


class CarrierStopOrder(models.Model):
    carrier_stop = models.ForeignKey(CarrierStop, on_delete=models.CASCADE)
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    def __str__(self):
        return "%d %s %s" % (self.order, self.carrier_stop, self.bus_stop)
