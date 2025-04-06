from django.urls import path

from message_receiver.views import api_message_receiver, message_status

urlpatterns = [
    # Message receiver endpoints
    path('messages/', api_message_receiver, name='api_message_receiver'),
    path('messages/<str:message_id>/', message_status, name='message_status'),
]
