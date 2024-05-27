from __future__ import absolute_import
from asgiref.sync import async_to_sync
from datetime import datetime
from celery import shared_task

from .telegram import telegram_sender
from .models import Reminder, Users, City
from .twilio import send_reminders
from .weather import check_precipitation
from dotenv import load_dotenv
load_dotenv()

# Мониторинг напоминаний
@shared_task
def process_reminders():
    now = datetime.now()
    # Получаем все напоминания, которые должны быть отправлены в текущее время или ранее
    reminders = Reminder.objects.filter(reminder_time__lte=now, sent=False)

    for reminder in reminders:
        number = Users.objects.get(reminder_id=reminder.id).number
        user = Users.objects.get(reminder_id=reminder.id).user
        reminder_time = reminder.reminder_time
        reminder_text = reminder.reminder_text

        if 'whatsapp' in number:
            # Отправляем уведомление
            send_reminders(reminder_text,
                           number,
                           user)
        else:
            async_to_sync(telegram_sender)(number, reminder_text, reminder_time, user )
        reminder.sent = True
        reminder.save()

# Мониторинг осадков
@shared_task
def check_precipitation_and_send_reminders():
    cities = City.objects.all()
    for city in cities:
        reminder_str_telegram, reminder_str_whatsapp, rain_probabilities = check_precipitation(city)
        if len(rain_probabilities) > 0:
            # Получаем все сообщения для данного города
            users = Users.objects.filter(city=city, rain_notifications_subscription=True)
            # Отправляем напоминание каждому пользователю
            for user in users:
                name = user.user
                number = user.number
                if 'whatsapp' in user.number:
                    send_reminders(reminder_text=reminder_str_whatsapp,
                                   number=number,
                                   user=None)
                else:
                    async_to_sync(telegram_sender)(user.number, reminder_str_telegram)