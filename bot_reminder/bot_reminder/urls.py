from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('whatsapp_bot.urls')),  # Включение маршрутов из reminder_bot
]
