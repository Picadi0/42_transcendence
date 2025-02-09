from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/online_status/<str:user_id>/", consumers.OnlineUsersConsumer.as_asgi()),
]
