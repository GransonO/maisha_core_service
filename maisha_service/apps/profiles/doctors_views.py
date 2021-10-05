from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
import uuid

import bugsnag
from rest_framework import views,  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from ..notifiers.FCM.fcm_requester import FcmCore
from .models import DoctorsProfiles, Speciality
from .serializers import DoctorProfileSerializer, SpecialitySerializer
from ..authentication.models import DoctorsActivation


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
            activate = DoctorsActivation.objects.filter(
                user_email=passed_data["email"],
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
                serializer = DoctorProfileSerializer(data=passed_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(user_id=user_reg_id, is_active=True)

                return Response({
                    "status": "success",
                    "user_id": user_reg_id,
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
            participant = DoctorsProfiles.objects.get(user_id=passed_data["user_id"])
            serializer = DoctorProfileSerializer(
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
            activate = DoctorsActivation.objects.filter(
                user_email=passed_data["email"],
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
                               "Login to receive calls. Thank you for registering with us".format(doctor_profile["fullname"])
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
            print("-------> {}".format(e))
            bugsnag.notify(
                Exception('Doctor active update: {}'.format(e))
            )
            return Response({
                "error": "{}".format(e),
                "status": "failed",
                "code": 0
            }, status.HTTP_200_OK)


class ProfilesAllView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = DoctorProfileSerializer

    def get_queryset(self):
        return DoctorsProfiles.objects.filter().order_by('createdAt')


class ProfileSpecificView(ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = DoctorProfileSerializer

    def get_queryset(self):
        return DoctorsProfiles.objects.filter(
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
        vector = SearchVector('speciality_name', 'speciality_description',)
        query = SearchQuery(passed_data["query"])
        doctor = Speciality.objects.annotate(
            rank=SearchRank(vector, query)
        ).filter(
            rank__gte=0.001
        ).order_by('-rank')
        return Response(list(doctor.values()), status.HTTP_200_OK)
