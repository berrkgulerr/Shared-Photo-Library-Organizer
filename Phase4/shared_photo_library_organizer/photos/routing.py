from . import consumers
from django.urls import re_path
websocket_urlpatterns = [
  re_path(r'websocket', consumers.SockConsumer.as_asgi()),
]