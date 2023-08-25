from django.urls import re_path
from stream import consumers

websocket_urlpatterns = [
    re_path(r'ws/stream/(?P<room_name>\w+)/$', consumers.VideoConsumer.as_asgi()),
]
