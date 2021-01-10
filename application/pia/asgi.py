"""
ASGI config for pia project.

It exposes the ASGI callable as a module-level variable named ``pia``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django

# Because Django Channels is stupid, we need to setup stuff here...
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pia.settings')
django.setup()

# ... and just then import rest of stuff
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import lobby.routing
import chat.routing

websocket_routing = chat.routing.websocket_urlpatterns + lobby.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_routing)
    ),
})
