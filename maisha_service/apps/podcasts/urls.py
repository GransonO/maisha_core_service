from django.urls import path
from .views import (
    PodcastsView, PodcastAllView, PodcastSpecificView, SearchPodcast)

urlpatterns = [
    path('',
         PodcastsView.as_view(),
         name="podcasts"
         ),

    path('<user_id>',
         PodcastSpecificView.as_view(),
         name="Podcast Specific"
         ),

    path('all/',
         PodcastAllView.as_view(),
         name="all Podcasts"
         ),

    path('search/',
         SearchPodcast.as_view(),
         name="Search Podcast"
         ),
]
