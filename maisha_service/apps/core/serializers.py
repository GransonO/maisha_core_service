import datetime

from .models import MaishaCore, SessionBounce, MaishaChats, CoreComplaints, DoctorPatientCreditTransfer, \
    ScheduledSessionsModel
from rest_framework import serializers
from ..profiles.models import DoctorsProfiles, PatientProfile


class MaishaCoreSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField('get_doctor')
    patient = serializers.SerializerMethodField('get_patient')

    class Meta:
        model = MaishaCore
        fields = '__all__'

    @staticmethod
    def get_doctor(obj):
        return DoctorsProfiles.objects.filter(user_id=obj.doctor_id).values()

    @staticmethod
    def get_patient(obj):
        return PatientProfile.objects.filter(user_id=obj.patient_id).values()


class CoreScheduledSerializer(serializers.ModelSerializer):

    scheduling = serializers.SerializerMethodField('get_schedule')

    class Meta:
        model = MaishaCore
        fields = '__all__'

    @staticmethod
    def get_schedule(obj):
        return ScheduledSessionsModel.objects.filter(session_id=obj.session_id).values()


class ScheduledSessionsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledSessionsModel
        fields = '__all__'


class MaishaAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaishaCore
        fields = '__all__'


class SessionBounceSerializer(serializers.ModelSerializer):

    class Meta:
        model = SessionBounce
        fields = '__all__'


class CoreChatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaishaChats
        fields = '__all__'


class CoreComplaintsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoreComplaints
        fields = '__all__'


class DoctorPatientCreditTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorPatientCreditTransfer
        fields = '__all__'

