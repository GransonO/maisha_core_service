from rest_framework import serializers
from ..profiles.models import DoctorsProfiles
from .models import Podcasts


class PodcastSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = Podcasts
        fields = '__all__'

    @staticmethod
    def get_doctor(obj):
        return DoctorsProfiles.objects.filter(user_id=obj.user_id).values()[0]
