# polls/routing.py
from django.urls import path
from .consumers import PollConsumer

websocket_urlpatterns = [
    path('ws/polls/<int:poll_id>/', PollConsumer.as_asgi()),
]