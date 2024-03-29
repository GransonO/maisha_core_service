import os
import uuid
import bugsnag
import time

from dotenv import load_dotenv
from django.db.models import Q
from django.utils import timezone

from datetime import datetime

from .agora.RtcTokenBuilder import RtcTokenBuilder, Role_Subscriber
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import MaishaCoreSerializer, SessionBounceSerializer, CoreChatsSerializer, CoreComplaintsSerializer, \
    ScheduledSessionsModelSerializer, CoreScheduledSerializer
from .models import MaishaCore, SessionBounce, MaishaChats, CoreComplaints
from ..profiles.models import PatientProfile, DoctorsProfiles, PatientsAccount, DoctorsAccount
from ..profiles.serializers import PatientsProfileSerializer, PatientsAccountSerializer, DoctorsAccountSerializer, \
    DoctorProfileSerializer
from ..notifiers.FCM.fcm_requester import FcmCore


class CoreRequest(views.APIView):
    """ Add a request to the therapist"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        try:
            the_id = uuid.uuid1()
            speciality = passed_data["speciality"]
            gender = passed_data["gender"]
            patient_id = passed_data["patient_id"]
            is_scheduled = passed_data["is_scheduled"]
            request_type = passed_data["type"]

            serializer = MaishaCoreSerializer(
                data=passed_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(session_id=the_id)

            # 1. Speciality (Dentist, Dermatologist) Can be optional
            doc_speciality = Q(speciality__exact="GENERAL")
            if speciality != "":
                doc_speciality = Q(speciality__exact=speciality)

            # 2. Based on Preference Filter (Male or female)
            doc_gender = Q()
            if passed_data["gender"] != "":
                doc_gender = Q(gender__exact=gender)

            patient = PatientProfile.objects.get(user_id=patient_id)
            patient_profile = PatientsProfileSerializer(patient).data

            if int(is_scheduled) == 0:  # Not Scheduled

                # Notify Doctors
                # 3. Doctor has to be online
                is_online = Q(is_online__exact=True)
                # Get the filtered doctors
                doctors = DoctorsProfiles.objects.filter(is_online & doc_speciality).values()

                return Response(
                    {
                        "success": True,
                        "patient_fcm": patient_profile["fcm"],
                        "session_id": str(the_id),
                        "doctors": list(doctors),
                        "message": "Posted successfully"
                    }, status.HTTP_200_OK
                )
            else:
                schedule_serializer = ScheduledSessionsModelSerializer(
                    data=passed_data, partial=True
                )
                schedule_serializer.is_valid(raise_exception=True)
                schedule_serializer.save(session_id=the_id)

                # send FCM to doctor Move to background work
                doctor = DoctorsProfiles.objects.get(user_id=passed_data["doctor_id"])
                profile = DoctorProfileSerializer(doctor).data
                FcmCore.maisha_schedule_notice(
                    profile["fcm"],
                    title_text="Maisha Consultation request",
                    body_text="You have a {} consultation request".format(request_type)
                )

                return Response(
                    {
                        "success": True,
                        "session_id": str(the_id),
                        "message": "Posted successfully"
                    }, status.HTTP_200_OK
                )

        except Exception as E:
            print("----------------Exception here---------------- {}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def put(request):
        try:
            passed_data = request.data
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])
            session_details = MaishaCoreSerializer(session).data

            if session_details["status"] == "ACCEPTED":
                return Response({
                    "success": False,
                    "message": "Request already taken"
                }, status.HTTP_200_OK)

            serializer = MaishaCoreSerializer(
                session, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Debounce Updater
            debounce_session = SessionBounce.objects.filter(
                session_id=passed_data["session_id"], doctor_id=passed_data["doctor_id"])
            debounce_session.update(doc_response=passed_data["status"])

            if passed_data["status"] == "ACCEPTED":
                # take Accepting doctor offline
                DoctorsProfiles.objects.filter(user_id=passed_data["doctor_id"]).update(is_online=False)
                # Sent only if Doc Accepts the request
                FcmCore.patient_core_notice(
                    fcm_token=passed_data["patient_fcm"],
                    message="Maisha request update",
                    doctor_id=passed_data["doctor_id"],
                    session_id=passed_data["session_id"],
                    status=passed_data["status"],
                )

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            print("---E--------------------{}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )


class CoreScheduledRequest(views.APIView):
    """ Add a request to the therapist"""
    permission_classes = [AllowAny]

    @staticmethod
    def put(request):
        try:
            passed_data = request.data
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])
            serializer = MaishaCoreSerializer(
                session, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            session_details = serializer.data

            if passed_data["status"] == "ACCEPTED":
                # take Accepting doctor offline
                patient = PatientProfile.objects.get(user_id=session_details["patient_id"])
                profile = PatientsProfileSerializer(patient).data
                # Sent only if Doc Accepts the request
                FcmCore.patient_core_notice(
                    fcm_token=profile["fcm"],
                    message="Maisha request update",
                    doctor_id=passed_data["doctor_id"],
                    session_id=passed_data["session_id"],
                    status=passed_data["status"],
                )

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('CoreScheduledRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )


class CoreSendRequest(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # Patient resend request to next doctor
        try:
            # Save the request
            passed_data = request.data

            session = MaishaCore.objects.get(session_id=passed_data["session_id"])
            serialized_session = MaishaCoreSerializer(session).data

            if serialized_session["status"] == "ACCEPTED":
                # Accepted or Cancelled
                return Response(
                    {
                        "success": True,
                        "message": "Request already updated"
                    }, status.HTTP_200_OK
                )
            else:
                serializer = SessionBounceSerializer(data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                print("---session--------------------{}".format(session))
                FcmCore.doctor_core_notice(
                    fcm_token=passed_data["doctor_fcm"],
                    message="Maisha {} request".format(passed_data["type"]),
                    description=passed_data["description"],
                    user_id=passed_data["patient_id"],
                    patient_fcm=passed_data["patient_fcm"],
                    session_id=passed_data["session_id"],
                    type=passed_data["type"]
                )

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            print("---Exception--------------------{}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )


class CoreAnalysis(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        try:
            passed_data = request.data
            all_requests = list(SessionBounce.objects.filter(doctor_id=passed_data["doctor_id"]))
            accepted_requests = []
            missed_requests = []
            for requests in all_requests:
                """Add based on doc_response"""

                if requests.doc_response == "ACCEPTED":
                    accepted_requests.append(requests)

                if requests.doc_response != "ACCEPTED":
                    missed_requests.append(requests)

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully",
                    "data": {
                        "numeral": {
                            "all": len(all_requests),
                            "accepted": len(accepted_requests),
                            "missed": len(missed_requests),
                        },
                    },
                }, status.HTTP_200_OK
            )
        except Exception as E:
            print("---Exception--------------------{}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )


class OnGoingSession(views.APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # Patient fetch ongoing session
        passed_data = request.data
        try:
            session = MaishaCore.objects.filter(
                patient_id=passed_data["patient_id"],
                status="ONGOING"
            ).values()
            return Response(list(session), status.HTTP_200_OK)

        except Exception as E:
            print("----------------Exception---------------- {}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "message": "error when fetching ongoing sessions"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def put(request):
        # Doctor fetch ongoing session
        passed_data = request.data
        try:
            session = MaishaCore.objects.filter(
                doctor_id=passed_data["doctor_id"],
                status="ONGOING"
            ).values()
            return Response(list(session), status.HTTP_200_OK)

        except Exception as E:
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return Response(
                {
                    "message": "error when fetching ongoing sessions"
                }, status.HTTP_200_OK
            )


class ScheduleSession(generics.ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = MaishaCoreSerializer

    def get_queryset(self):
        if 'patient' in self.request.path:
            # request for patients
            return MaishaCore.objects.filter(
                patient_id=self.kwargs['patient_id'],
                is_completed=False,
                status="ACCEPTED",
                is_scheduled=1
                )
        else:
            return MaishaCore.objects.filter(
                doctor_id=self.kwargs['doctor_id'],
                is_completed=False,
                status="ACCEPTED",
                is_scheduled=1
            )


class RateSession(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # Patient Posting rating and account balance
        try:
            # Save the request
            passed_data = request.data
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])

            if passed_data["is_doctor"] == 1:
                if session.is_complete is False:
                    # Doctor ended session before patient
                    return Response(
                        {
                            "success": False,
                            "code": "PATIENT_NOT_COMPLETE",
                            "message": "Please wait for the patient to complete the session first"
                        }, status.HTTP_200_OK
                    )
                else:
                    # Transfer funds if rating above
                    if float(passed_data["session_doctor_rating"]) > 3:
                        # Update Patients amount
                        patient_account = PatientsAccount.objects.get(
                            patient_id=session.patient_id)

                        patient_serializer = PatientsAccountSerializer(
                            patient_account, data={
                                "aggregate_available_amount": patient_account.aggregate_available_amount - session.session_value,
                                "aggregate_used_amount": patient_account.aggregate_used_amount + session.session_value,
                                "last_transaction_date": timezone.now()
                            }, partial=True)
                        patient_serializer.is_valid(raise_exception=True)
                        patient_serializer.save()

                        # Update Doctors amount
                        doctors_account = DoctorsAccount.objects.get(
                            doctor_id=session.doctor_id)

                        doctors_serializer = DoctorsAccountSerializer(
                            doctors_account, data={
                                "aggregate_available_amount": doctors_account.aggregate_available_amount + session.session_value,
                                "aggregate_collected_amount": doctors_account.aggregate_collected_amount + session.session_value,
                                "last_transaction_date": timezone.now()
                            }, partial=True)
                        doctors_serializer.is_valid(raise_exception=True)
                        doctors_serializer.save()

                        MaishaCore.objects.filter(session_id=passed_data["session_id"]).update(session_settled=True)

            serializer = MaishaCoreSerializer(session, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully",
                    "code": "DONE",
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('Core Update Put: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def put(request):
        # Doctors rating
        try:
            # Save the request
            passed_data = request.data
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])

            serializer = MaishaCoreSerializer(session, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            DoctorsProfiles.objects.filter(user_id=session.doctor_id).update(is_online=True)
            return Response(
                {
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('Core Update Put: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )


class GetUserRequests(generics.ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = MaishaCoreSerializer

    def get_queryset(self):
        return MaishaCore.objects.filter(
            patient_id=self.kwargs['patient_id']
            )


class SpecificRequest(generics.ListAPIView):
    """Get a user specific appointments"""
    permission_classes = [AllowAny]
    serializer_class = MaishaCoreSerializer

    def get_queryset(self):
        return MaishaCore.objects.filter(
            session_id=self.kwargs['session_id']
            ).order_by('createdAt')


class TokenGenerator(views.APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data

        load_dotenv()
        app_id = os.environ['MAISHA_AGORA_APP_ID']
        app_certificate = os.environ['MAISHA_AGORA_APP_CERTIFICATE']
        channel_name = passed_data["channel_name"]
        user_account = passed_data["callUid"]
        expire_time_in_seconds = 7200
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expire_time_in_seconds

        if passed_data["is_patient"] == 1:
            MaishaCore.objects.filter(session_id=channel_name).update(status="ONGOING")

        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, user_account, Role_Subscriber, privilege_expired_ts)
        return Response({'token': token, 'appID': app_id}, status.HTTP_200_OK)


class CoreChats(views.APIView):
    """Chat features"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # New message posted
        try:
            passed_data = request.data
            serializer = CoreChatsSerializer(
                data=passed_data, partial=True
            )
            serializer.is_valid()
            serializer.save()

            chats = MaishaChats.objects.filter(session_id=passed_data["session_id"])
            return Response(
                {
                    "data": list(chats.values()),
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('CoreChat Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def put(request):
        # Update message
        try:
            passed_data = request.data
            chat = MaishaChats.objects.get(message_id=passed_data["message_id"])
            serializer = CoreChatsSerializer(
                chat, data=passed_data, partial=True
            )
            serializer.is_valid()
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Updated successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('CoreChat Put: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Update failed"
                }, status.HTTP_200_OK
            )


class ChatRetriever(generics.ListAPIView):
    # get all session messages
    permission_classes = [AllowAny]
    serializer_class = CoreChatsSerializer

    def get_queryset(self):
        return MaishaChats.objects.filter(
            session_id=self.kwargs['session_id']
        ).order_by('createdAt')


class Complaints(views.APIView):
    """Chat features"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # New message posted
        try:
            passed_data = request.data
            complaint_uuid = uuid.uuid1()
            serializer = CoreComplaintsSerializer(
                data=passed_data, partial=True
            )
            serializer.is_valid()
            serializer.save(complaint_id=complaint_uuid)

            return Response(
                {
                    "success": True,
                    "message": "Posted successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('CoreComplaints Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def put(request):
        # Update message
        try:
            passed_data = request.data
            complaint = CoreComplaints.objects.get(complaint_id=passed_data["complaint_id"])
            serializer = CoreComplaintsSerializer(
                complaint, data=passed_data, partial=True
            )
            serializer.is_valid()
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Updated successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('CoreComplaint Put: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Update failed"
                }, status.HTTP_200_OK
            )


class ComplaintsRetriever(generics.ListAPIView):
    # get all session messages
    permission_classes = [AllowAny]
    serializer_class = CoreComplaintsSerializer

    def get_queryset(self):
        return CoreComplaints.objects.filter(
            session_id=self.kwargs['session_id']
        ).order_by('createdAt')
