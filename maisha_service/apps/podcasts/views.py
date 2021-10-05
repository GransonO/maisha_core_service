from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
import uuid

import bugsnag
from rest_framework import views,  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from .models import Podcasts
from .serializers import PodcastSerializer
from ..subscriptions.models import Subscription
from ..notifiers.FCM.fcm_requester import FcmCore
from ..profiles.models import PatientProfile


class PodcastsView(views.APIView):
    """
        Add Profiles details and save in DB
    """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add Profiles to DB """
        passed_data = request.data
        try:
            pod_id = uuid.uuid1()
            # Save data to DB
            pods_data = PodcastSerializer(
                data=passed_data, partial=True
            )
            pods_data.is_valid()
            pods_data.save(podcast_id=pod_id)

            # *** Move this section to background
            # send FCM TO ALL SUBSCRIBERS
            subscribers = Subscription.objects.filter(doctor_id=passed_data["user_id"])
            all_tokens = []
            for subscriber in list(subscribers):
                resource = PatientProfile.objects.filter(user_id=subscriber.patient_id).first()
                all_tokens.append(resource.fcm)

            FcmCore.subscribers_notice(
                all_tokens, "A new podcast for you", "podcast", pod_id, passed_data["uploaded_by"]
            )
            # *** Move this section to background

            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Podcast Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        """Add Subscriptions"""
        passed_data = request.data
        try:
            # Save data to DB
            serialized = Podcasts.objects.get(podcast_id=passed_data["podcast_id"])
            pods_data = PodcastSerializer(
                serialized, data=passed_data, partial=True
            )
            pods_data.is_valid()
            pods_data.save(podcast_id=uuid.uuid1())
            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Podcast PUT: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class PodcastAllView(ListAPIView):
    """Get all Podcasts"""
    permission_classes = [AllowAny]
    serializer_class = PodcastSerializer

    def get_queryset(self):
        return Podcasts.objects.filter().order_by('createdAt')


class PodcastSpecificView(ListAPIView):
    """Get a user specific podcasts"""
    permission_classes = [AllowAny]
    serializer_class = PodcastSerializer

    def get_queryset(self):
        return Podcasts.objects.filter(
            user_id=self.kwargs['user_id']
            ).order_by('createdAt')


class SearchPodcast(views.APIView):
    """Search for podcasts using keys"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        vector = SearchVector('title', 'details', 'interest')
        query = SearchQuery(passed_data["query"])
        podcast = Podcasts.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank')
        return Response(list(podcast.values()), status.HTTP_200_OK)
