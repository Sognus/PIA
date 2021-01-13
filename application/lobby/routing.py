from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/lobby/chat', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/lobby/requests', consumers.RequestConsumer.as_asgi()),
]