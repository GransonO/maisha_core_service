"""
ASGI config for maisha_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import maisha_service.apps.ws_connect.routing as route

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maisha_service.settings')
django.setup()

application = ProtocolTypeRouter({
    # For HTTP Requests
    "http": get_asgi_application(),

    # For Web Sockets
    'websocket': AuthMiddlewareStack(
        URLRouter(
            route.websocket_urlpatterns
        )
    ),
})
