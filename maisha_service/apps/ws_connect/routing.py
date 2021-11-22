# from django.conf.urls import url
from django.urls import re_path
from maisha_service.apps.ws_connect.chat_socket import SocketChat
from maisha_service.apps.ws_connect.core_socket import SocketCore

"""All doctors and users connected to the service get responses, Frontend checks if it can be resolved"""

websocket_urlpatterns = [
    # Connect to request room
    re_path(r'ws_core/$', SocketCore.as_asgi()),

    # Connect to individual chat room
    re_path(r'ws_chat/(?P<room_name>\w+)/$', SocketChat.as_asgi()),
]
