from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import (DoctorsProfiles, PatientProfile, Notifiers, PreferredDoctors,
                     Allergies, RecurrentIssues, Dependants, Speciality,
                     PatientsAccount, DoctorsAccount,)


class DoctorProfileSerializer(ModelSerializer):

    doctor_account_details = SerializerMethodField('get_doctor_account_details')

    class Meta:
        model = DoctorsProfiles
        fields = '__all__'

    @staticmethod
    def get_doctor_account_details(obj):
        return list(
            DoctorsAccount.objects.filter(doctor_id=obj.user_id).values()
        )


class PatientsProfileSerializer(ModelSerializer):
    patient_allergies = SerializerMethodField('get_patients_allergies')
    patient_recurrent_issues = SerializerMethodField('get_patients_recurrent_issues')
    patient_dependants = SerializerMethodField('get_patients_dependants')
    patient_notifiers = SerializerMethodField('get_patients_notifiers')
    patient_preferred_doctors = SerializerMethodField('get_patients_preferred_doctors')
    patient_account_details = SerializerMethodField('get_patient_account_details')

    class Meta:
        model = PatientProfile
        fields = '__all__'

    @staticmethod
    def get_patients_allergies(obj):
        return list(
            Allergies.objects.filter(patient_id=obj.user_id).values()
        )

    @staticmethod
    def get_patient_account_details(obj):
        return list(
            PatientsAccount.objects.filter(patient_id=obj.user_id).values()
        )

    @staticmethod
    def get_patients_recurrent_issues(obj):
        return list(
            RecurrentIssues.objects.filter(patient_id=obj.user_id).values()
        )

    @staticmethod
    def get_patients_dependants(obj):
        return list(
            Dependants.objects.filter(patient_id=obj.user_id).values()
        )

    @staticmethod
    def get_patients_notifiers(obj):
        return list(
            Notifiers.objects.filter(patient_id=obj.user_id).values()
        )

    @staticmethod
    def get_patients_preferred_doctors(obj):
        return list(
            PreferredDoctors.objects.filter(patient_id=obj.user_id).values()
        )


class AllergiesSerializer(ModelSerializer):

    class Meta:
        model = Allergies
        fields = '__all__'


class RecurrentIssuesSerializer(ModelSerializer):

    class Meta:
        model = RecurrentIssues
        fields = '__all__'


class DependantsSerializer(ModelSerializer):

    profile = SerializerMethodField('get_dependant_profile')

    class Meta:
        model = Dependants
        fields = '__all__'

    @staticmethod
    def get_dependant_profile(obj):
        return PatientProfile.objects.filter(user_id=obj.relative_id).values()


class NotifierSerializer(ModelSerializer):

    profile = SerializerMethodField('get_dependant_profile')

    class Meta:
        model = Notifiers
        fields = '__all__'

    @staticmethod
    def get_dependant_profile(obj):
        return PatientProfile.objects.filter(user_id=obj.relative_id).values()


class SpecialitySerializer(ModelSerializer):

    class Meta:
        model = Speciality
        fields = '__all__'


class PatientsAccountSerializer(ModelSerializer):

    class Meta:
        model = PatientsAccount
        fields = '__all__'


class DoctorsAccountSerializer(ModelSerializer):

    class Meta:
        model = DoctorsAccount
        fields = '__all__'

