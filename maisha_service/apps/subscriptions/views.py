import bugsnag
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SubscriptionSerializer
from ..profiles.models import DoctorsProfiles
from ..profiles.serializers import DoctorProfileSerializer
from .models import Subscription


class Subscribe(views.APIView):
    """ Add a request to the therapist"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        try:
            passed_data = request.data
            value = Subscription.objects.filter(
                doctor_id=passed_data["doctor_id"],
                patient_id=passed_data["patient_id"],
            )
            if len(value) > 0:
                # Update old entry
                session = Subscription.objects.get(
                    doctor_id=passed_data["doctor_id"],
                    patient_id=passed_data["patient_id"],
                )
                serializer = SubscriptionSerializer(
                    session, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # Save new entry
                serializer = SubscriptionSerializer(
                    data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Subscribed successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('Subscribed Post: {}'.format(E))
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
            session = Subscription.objects.get(
                doctor_id=passed_data["doctor_id"],
                patient_id=passed_data["patient_id"],
            )
            serializer = SubscriptionSerializer(
                session, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Update successfully"
                }, status.HTTP_200_OK
            )
        except Exception as E:
            bugsnag.notify(
                Exception('Subscription Post: {}'.format(E))
            )
            return Response(
                {
                    "success": False,
                    "message": "Posting failed"
                }, status.HTTP_200_OK
            )

    @staticmethod
    def get(request):
        passed_data = request.data
        subscriptions = Subscription.objects.filter(
            patient_id=passed_data["patient_id"],
        )
        value = []
        for item in list(subscriptions):
            doctor = DoctorsProfiles.objects.get(user_id=item.doctor_id)
            value.append({
                "doctor": DoctorProfileSerializer(doctor).data,
                "subscriptions": {
                    "blogs": item.subscribed_blogs,
                    "podcasts": item.subscribed_pods,
                }
            })

        return Response(
            {
                "success": True,
                "body": value,
                "message": "Update successfully"
            }, status.HTTP_200_OK
        )


class SpecificSub(views.APIView):
    """Get users subscribe"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        subscriptions = Subscription.objects.filter(
            patient_id=passed_data["patient_id"],
        )
        value = []
        for item in list(subscriptions):
            doctor = DoctorsProfiles.objects.get(user_id=item.doctor_id)
            value.append({
                "doctor": DoctorProfileSerializer(doctor).data,
                "subscriptions": {
                    "blogs": item.subscribed_blogs,
                    "podcasts": item.subscribed_pods,
                }
            })

        return Response(
            {
                "success": True,
                "body": value,
                "message": "Collected successfully"
            }, status.HTTP_200_OK
        )
