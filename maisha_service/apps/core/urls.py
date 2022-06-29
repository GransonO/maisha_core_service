from django.urls import path
from .views import (CoreRequest, TokenGenerator, CoreAnalysis, ComplaintsRetriever,
                    SpecificRequest, GetUserRequests, ChatRetriever, OnGoingSession,
                    CoreSendRequest, RateSession, CoreChats, Complaints)

urlpatterns = [

    path('',
         CoreRequest.as_view(),
         name="Core Request"
         ),

    path('send/',
         CoreSendRequest.as_view(),
         name="Core Send Out Request"
         ),

    path('<session_id>',
         SpecificRequest.as_view(),
         name="Specific Request"
         ),

    path('ongoing_session/',
         OnGoingSession.as_view(),
         name="Check Ongoing Session"
         ),

    path('patient/<patient_id>',
         GetUserRequests.as_view(),
         name="Get User Requests"
         ),

    path('token/',
         TokenGenerator.as_view(),
         name="Token Generator"
         ),

    path('rating/',
         RateSession.as_view(),
         name="Rate Session"
         ),

    path('doc/rating/',
         RateSession.as_view(),
         name="Rate Session"
         ),

    path('chats/',
         CoreChats.as_view(),
         name="Core Chats"
         ),

    path('chats/<session_id>',
         ChatRetriever.as_view(),
         name="All Session Chats"
         ),

    path('analysis/',
         CoreAnalysis.as_view(),
         name="Core Analysis"
         ),

    path('complaints/',
         Complaints.as_view(),
         name="Complaints"
         ),

    path('complaints/<session_id>',
         ComplaintsRetriever.as_view(),
         name="Complaints Retriever"
         ),
]
