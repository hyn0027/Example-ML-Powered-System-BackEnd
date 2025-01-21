from django.urls import path
from aeye.consumers import ProcessConsumer

websocket_urlpatterns = [
    path("ws/process/", ProcessConsumer.as_asgi()),
]
