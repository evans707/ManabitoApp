import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import scraping.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            scraping.routing.websocket_urlpatterns
        )
    ),
})