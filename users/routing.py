from django.urls import path, include
from django.urls import re_path
from .consumer import ChatConsumer

# the empty string routes to ChatConsumer, which manages the chat functionality.
websocket_urlpatterns = [
    re_path(r'ws/chat/', ChatConsumer.as_asgi()),
    # Add more WebSocket URL patterns as needed
]


