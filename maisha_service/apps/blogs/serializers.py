from rest_framework import serializers
from .models import BlogsDB, Comments
from ..profiles.models import DoctorsProfiles


class CommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField('get_blog_comments')
    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = BlogsDB
        fields = '__all__'

    @staticmethod
    def get_blog_comments(obj):
        return list(
                Comments.objects.filter(blog_id=obj.blog_id).values()
        )

    @staticmethod
    def get_doctor(obj):
        return DoctorsProfiles.objects.filter(user_id=obj.uploader_id).values()[0]
