# Create your views here.
import uuid

import bugsnag
from rest_framework import views,  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from ..notifiers.FCM.fcm_requester import FcmCore
from ..profiles.models import PatientProfile
from ..subscriptions.models import Subscription
from .models import BlogsDB, Comments
from .serializers import BlogSerializer, CommentsSerializer


class Blog(views.APIView):
    """
        Add Blog details and save in DB
    """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add Blog to DB """
        passed_data = request.data
        try:
            blg_id = uuid.uuid1()
            serializer = BlogSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(blog_id=blg_id)

            # *** Move this section to background
            # send FCM TO ALL SUBSCRIBERS
            subscribers = Subscription.objects.filter(doctor_id=passed_data["uploader_id"])
            all_tokens = []
            for subscriber in list(subscribers):
                resource = PatientProfile.objects.filter(user_id=subscriber.patient_id).first()
                all_tokens.append(resource.fcm)

            FcmCore.subscribers_notice(
                all_tokens, "A new blog for you", "blog", blg_id, passed_data["uploaded_by"]
            )
            # *** Move this section to background

            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Blog Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        passed_data = request.data
        # Check This later
        try:
            blog = BlogsDB.objects.get(blog_id=passed_data["blog_id"])
            serializer = BlogSerializer(blog, data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                    "status": "success",
                    "code": 1
                    }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Blog update: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class BlogAllView(ListAPIView):
    """Get all blogs"""
    permission_classes = [AllowAny]
    serializer_class = BlogSerializer

    def get_queryset(self):
        return BlogsDB.objects.filter().order_by('-createdAt')


class BlogSpecificView(ListAPIView):
    """Get a user specific blog"""
    permission_classes = [AllowAny]
    serializer_class = BlogSerializer

    def get_queryset(self):
        return BlogsDB.objects.filter(
            blog_id=self.kwargs['blog_id']
            ).order_by('-createdAt')


class BlogUserSpecific(ListAPIView):
    """Get a trainer specific"""
    permission_classes = [AllowAny]
    serializer_class = BlogSerializer

    def get_queryset(self):
        return BlogsDB.objects.filter(
            uploader_id=self.kwargs['uploader_id']
            ).order_by('-createdAt')


class BlogComments(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add Comments to DB """
        print("============ Blog posting is on")
        passed_data = request.data
        try:
            serializer = CommentsSerializer(data=passed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": "success",
                "code": 1
            }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Blog Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)


class AllBlogComments(ListAPIView):
    """Get all comments"""
    permission_classes = [AllowAny]
    serializer_class = CommentsSerializer

    def get_queryset(self):
        return Comments.objects.filter(
            blog_id=self.kwargs['blog_id']
        ).order_by('-createdAt')


class SearchBlog(views.APIView):
    """Search for blogs using keys"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        vector = SearchVector('title', 'body', 'interest')
        query = SearchQuery(passed_data["query"])
        blog = BlogsDB.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank')
        return Response(list(blog.values()), status.HTTP_200_OK)
