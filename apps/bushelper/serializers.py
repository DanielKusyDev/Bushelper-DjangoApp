from rest_framework import serializers

from apps.bushelper.models import BusStop


class BusStopSerializer(serializers.ModelSerializer):
    direction = serializers.StringRelatedField()

    class Meta:
        model = BusStop
        fields = (
            'pk', 'mpk_street', 'fremiks_alias', 'direction'
        )



# class CourseSerializer(serializers.ModelSerializer):
#     carrier = serializers.StringRelatedField()
#     bus_stop = serializers.StringRelatedField()
#     departure = serializers.StringRelatedField()
#     line = serializers.StringRelatedField()
#     direction = serializers.StringRelatedField()
#
#     class Meta:
#         model = Course
#         fields = ['pk', 'course_type', 'direction', 'line', 'carrier', 'bus_stop', 'departure']
#
#
# class BusStopSerializer(serializers.ModelSerializer):
#     direction = serializers.StringRelatedField()
#
#     class Meta:
#         model = BusStop
#         fields = ['url', 'id', 'mpk_street', 'fremiks_alias', 'direction']
#
#
# class CarrierStopSerializer(serializers.ModelSerializer):
#     carrier = serializers.StringRelatedField()
#     line = serializers.StringRelatedField()
#     direction = serializers.StringRelatedField()
#     bus_stop = serializers.SerializerMethodField(read_only=True)
#
#     def get_bus_stop(self, model):
#         return [bus_stop for bus_stop in CarrierStopOrder.objects.filter(carrier_stop=model).order_by('order').values_list('bus_stop', flat=True)]
#         # return [BusStop.objects.filter(pk=bus_stop).values_list('mpk_street', flat=True) for bus_stop in CarrierStopOrder.objects.filter(carrier_stop=model).order_by('order').values_list('bus_stop', flat=True)]
#
#     class Meta:
#         model = CarrierStop
#         fields = ['id', 'carrier', 'line', 'direction', 'bus_stop']
#
#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     courses = serializers.HyperlinkedRelatedField(many=True, view_name='courses', read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'bus_stops')
