from django.urls import path
from .views import handle_incoming_message, index

urlpatterns = [
    path('', index, name='home'),
    path('webhook/', handle_incoming_message, name='webhook'),
]