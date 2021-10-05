from django.urls import path
from .views import Subscribe, SpecificSub

urlpatterns = [

    path('',
         Subscribe.as_view(),
         name="Subscribe"
         ),

    path('specific/',
         SpecificSub.as_view(),
         name="Subscribe"
         ),
]
