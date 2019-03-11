from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.db.models.signals import post_save

from apps.bushelper.models import BusStop


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=CASCADE, verbose_name='user')
    avatar = models.ImageField(null=True, blank=True, verbose_name='avatar')
    description = models.CharField(max_length=100, null=True, blank=True, verbose_name='description')
    favourites = models.ManyToManyField(to=BusStop, through='Waypoint', through_fields=('profile', 'bus_stop'),
                                        verbose_name='favourites')

    def __str__(self):
        return self.user.__str__()


class Waypoint(models.Model):
    profile = models.ForeignKey(to=Profile, on_delete=CASCADE, verbose_name='profile')
    bus_stop = models.ForeignKey(to=BusStop, on_delete=CASCADE, verbose_name='bus_stop')
    label = models.CharField(max_length=127, null=True, blank=True, verbose_name='l abel')


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = Profile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)