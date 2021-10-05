from django.urls import path
from .views import (
     Blog, BlogUserSpecific, SearchBlog,
     BlogAllView, BlogSpecificView,
     BlogComments, AllBlogComments
     )

urlpatterns = [
    path('',
         Blog.as_view(),
         name="Blog"
         ),

    path('<blog_id>',
         BlogSpecificView.as_view(),
         name="Specific Blogs"
         ),

    path('user/<uploader_id>',
         BlogUserSpecific.as_view(),
         name="User Blogs"
         ),

    path('all/',
         BlogAllView.as_view(),
         name="All Blogs"
         ),

    path('search/',
         SearchBlog.as_view(),
         name="Search Blog"
         ),

    path('comments/',
         BlogComments.as_view(),
         name="Post Comments"
         ),

    path('comments/all/<blog_id>',
         AllBlogComments.as_view(),
         name="Post Comments"
         )
]
