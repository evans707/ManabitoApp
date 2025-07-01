from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scraping-status/$', consumers.ScrapingStatusConsumer.as_asgi()),
]