from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/chat', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/game', consumers.GameConsumer.as_asgi()),
]
