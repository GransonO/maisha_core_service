from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
import uuid

import bugsnag
from django.db.models import Q
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from maisha_service.apps.notifiers.EMAILS.profile_email import ProfileEmail
from ..notifiers.FCM.fcm_requester import FcmCore
from .models import DoctorsProfiles, Speciality, DoctorsAccount, PatientsAccount, PatientProfile, RecurrentIssues, \
    Dependants, Notifiers, Allergies
from .serializers import DoctorProfileSerializer, SpecialitySerializer, PatientsProfileSerializer, AllergiesSerializer, \
    RecurrentIssuesSerializer, DependantsSerializer, NotifierSerializer
from ..authentication.models import UserActivation


class Profiles(views.APIView):
    """
        Add Profiles details and save in DB
    """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add Profiles to DB """
        passed_data = request.data
        try:
            activate = UserActivation.objects.filter(
                user_email=passed_data["email"].strip(),
                user_phone=passed_data["phone_number"].strip(),
                activation_code=int(passed_data["activation_code"])
            )
            if activate.count() < 1:
                return Response({
                    "status": "Failed",
                    "code": 0,
                    "message": "Update failed, wrong activation code passed"
                }, status.HTTP_200_OK)
            else:
                # Save data to DB
                user_reg_id = uuid.uuid1()
                if passed_data["isDoctor"] == "true":
                    serializer = DoctorProfileSerializer(data=passed_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(user_id=user_reg_id, is_active=True)
                    doc_account = DoctorsAccount(
                        doctor_id=user_reg_id
                    )
                    doc_account.save()
                else:
                    serializer = PatientsProfileSerializer(data=passed_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(user_id=user_reg_id, is_active=True)
                    accounts_details = PatientsAccount(
                        patient_id=user_reg_id
                    )
                    accounts_details.save()

                ProfileEmail.send_registration_email(passed_data["fullname"].strip(), passed_data["email"].strip())
                return Response({
                    "status": "success",
                    "user_id": user_reg_id,
                    "profile": serializer.data,
                    "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('Profile Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "Profile creation failed",
                "code": 0
            }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        passed_data = request.data
        # Check This later
        try:
            if passed_data["isDoctor"] == "true":
                participant = DoctorsProfiles.objects.get(user_id=passed_data["user_id"])
                serializer = DoctorProfileSerializer(
                    participant, data=passed_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                participant = PatientProfile.objects.get(user_id=passed_data["patient_id"])
                serializer = PatientsProfileSerializer(
                    participant, data=passed_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
            }, status.HTTP_200_OK)


class CodeVerify(views.APIView):
    """Verify User code"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add Profiles to DB """
        passed_data = request.data
        try:
            activate = UserActivation.objects.filter(
                user_email=passed_data["email"].strip(),
                user_phone=passed_data["phone"],
                activation_code=int(passed_data["activation_code"])
            )
            if activate.count() < 1:
                return Response({
                    "status": "Failed",
                    "code": 0,
                    "message": "Update failed, wrong activation code passed"
                }, status.HTTP_200_OK)
            else:
                return Response({
                    "status": "success",
                    "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Code Verification: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
            }, status.HTTP_200_OK)


class DoctorValidation(views.APIView):
    """Activate or Deactivate doctor"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        try:
            doctor = DoctorsProfiles.objects.get(user_id=passed_data["user_id"])
            doctor_serializer = DoctorProfileSerializer(
                doctor, passed_data, partial=True
            )
            doctor_serializer.is_valid()
            doctor_serializer.save()

            doctor_profile = DoctorProfileSerializer(doctor).data

            if passed_data["status"] == "1":
                message_body = "Hello {}, your account has been verified. " \
                               "Thank you for registering with us." \
                               "Login to receive calls. ".format(doctor_profile["fullname"])
            else:
                message_body = "Hello {}, your account has been deactivated. " \
                               "Contact support for more information".format(doctor_profile["fullname"])

            FcmCore.doctor_validation_notice(
                all_tokens=[doctor_profile["fcm"]],
                message=message_body,
            )

            return Response(
                {
                    "status": "success"
                }, status.HTTP_200_OK
            )
        except Exception as e:
            bugsnag.notify(
                Exception('Doctor active update: {}'.format(e))
            )
            return Response({
                "error": "{}".format(e),
                "status": "failed",
                "code": 0
            }, status.HTTP_200_OK)


class DoctorAllProfileView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = DoctorProfileSerializer

    def get_queryset(self):
        return DoctorsProfiles.objects.filter().order_by('createdAt')


class PatientAllProfileView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = PatientsProfileSerializer

    def get_queryset(self):
        return PatientProfile.objects.filter().order_by('createdAt')


class DoctorProfileSpecificView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = DoctorProfileSerializer

    def get_queryset(self):
        return DoctorsProfiles.objects.filter(
            user_id=self.kwargs['userId']
        ).order_by('createdAt')


class PatientProfileSpecificView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = PatientsProfileSerializer

    def get_queryset(self):
        return PatientProfile.objects.filter(
            user_id=self.kwargs['userId']
            ).order_by('createdAt')


class SearchDoctor(views.APIView):
    """Search for doctor using keys"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        vector = SearchVector('fullname', 'registered_hospital', 'speciality', 'email')
        query = SearchQuery(passed_data["query"])
        doctor = DoctorsProfiles.objects.annotate(
            rank=SearchRank(vector, query)
        ).filter(
            rank__gte=0.001
        ).order_by('-rank')
        return Response(list(doctor.values()), status.HTTP_200_OK)


class SpecialityView(views.APIView):
    """Allergies"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """"Add new allergy"""
        passed_data = request.data
        try:
            # Save data to DB
            speciality_id = uuid.uuid1()
            serializer = SpecialitySerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(entry_id=speciality_id, is_active=True)

            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('Speciality Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "message": "Speciality creation failed",
                "code": 0
            }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        # Remove from Allergies (Status inactive)
        passed_data = request.data
        try:
            participant = Speciality.objects.get(entry_id=passed_data["entry_id"])
            serializer = SpecialitySerializer(
                participant, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Put Speciality: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
            }, status.HTTP_200_OK)


class SpecialitySearch(views.APIView):
    """Search for doctor using keys"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data

        speciality_name = Q(speciality__icontains=passed_data["query"])
        speciality_description = Q(speciality_description__icontains=passed_data["query"])

        doctors = DoctorsProfiles.objects.filter(speciality_name | speciality_description).values()
        return Response(list(doctors), status.HTTP_200_OK)


class AllergiesView(views.APIView):
    """Allergies"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """"Add new allergy"""
        passed_data = request.data
        try:
            # Save data to DB
            allergy_reg_id = uuid.uuid1()
            serializer = AllergiesSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(allergy_id=allergy_reg_id, is_active=True)

            return Response({
                "status": "success",
                "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('Profile Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "message": "Profile creation failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        # Remove from Allergies (Status inactive)
        passed_data = request.data
        try:
            participant = Allergies.objects.get(allergy_id=passed_data["allergy_id"])
            serializer = AllergiesSerializer(
                participant, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                    "status": "success",
                    "code": 1
                    }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Put: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class AllergiesSpecificView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = AllergiesSerializer

    def get_queryset(self):
        return Allergies.objects.filter(patient_id=self.kwargs["patient_id"], is_active=True).order_by('createdAt')


class RecurrentIssuesView(views.APIView):
    """Allergies"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """"Add new allergy"""
        passed_data = request.data
        try:
            # Save data to DB
            recurrent_issue_id = uuid.uuid1()
            serializer = RecurrentIssuesSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(issue_id=recurrent_issue_id, is_active=True)

            return Response({
                "status": "success",
                "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('RecurrentIssues Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "message": "RecurrentIssues creation failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        # Remove from Allergies (Status inactive)
        passed_data = request.data
        try:
            participant = RecurrentIssues.objects.get(issue_id=passed_data["issue_id"])
            serializer = RecurrentIssuesSerializer(
                participant, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                    "status": "success",
                    "code": 1
                    }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Put: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class RecurrentIssuesSpecificView(ListAPIView):
    """Get a user specific RecurrentIssues"""
    permission_classes = [AllowAny]
    serializer_class = RecurrentIssuesSerializer

    def get_queryset(self):
        return RecurrentIssues.objects.filter(patient_id=self.kwargs["patient_id"], is_active=True).order_by('createdAt')


class DependantsView(views.APIView):
    """Dependants"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """"Add new allergy"""
        passed_data = request.data
        try:
            # Save data to DB
            entry_id = uuid.uuid1()
            serializer = DependantsSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(entry_id=entry_id, is_active=True)

            return Response({
                "status": "success",
                "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('Dependants Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "message": "Dependant creation failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        # Remove from Dependants (Status inactive)
        passed_data = request.data
        try:
            dependant = Dependants.objects.get(entry_id=passed_data["entry_id"])
            serializer = DependantsSerializer(
                dependant, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                    "status": "success",
                    "code": 1
                    }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Dependant Put: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class DependantSpecificView(ListAPIView):
    """Get a user Dependants"""
    permission_classes = [AllowAny]
    serializer_class = DependantsSerializer

    def get_queryset(self):
        return Dependants.objects.filter(patient_id=self.kwargs["patient_id"], is_active=True).order_by('createdAt')


class NotifierView(views.APIView):
    """Notifier"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """"Add new Notifier"""
        passed_data = request.data
        try:
            # Save data to DB
            entry_id = uuid.uuid1()
            serializer = NotifierSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(entry_id=entry_id, is_active=True)

            return Response({
                "status": "success",
                "code": 1
                }, status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('Notifier Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "message": "Notifier creation failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        # Remove from Notifier (Status inactive)
        passed_data = request.data
        try:
            notifier = Notifiers.objects.get(entry_id=passed_data["entry_id"])
            serializer = NotifierSerializer(
                notifier, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                    "status": "success",
                    "code": 1
                    }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Profile Notifier Put: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class NotifierSpecificView(ListAPIView):
    """Get a user specific RecurrentIssues"""
    permission_classes = [AllowAny]
    serializer_class = NotifierSerializer

    def get_queryset(self):
        return Notifiers.objects.filter(patient_id=self.kwargs["patient_id"], is_active=True).order_by('createdAt')


class RelativeSearch(views.APIView):
    """Search profile using email"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        vector = SearchVector('email')
        query = SearchQuery(passed_data["query"])
        relative = PatientProfile.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank')
        return Response(list(relative.values()), status.HTTP_200_OK)
