import sys
import urllib.parse
from django.http import HttpResponse
import datetime as dt
from dateutil import parser as date_parser
from .gpt_responder import text_converting
from .weather import forecast_precipitation
from .twilio import send_confirmation
from .models import City, Users
from .tasks import process_reminders, check_precipitation_and_send_reminders
from .services import save_incoming_message, save_reminder

import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
from dotenv import load_dotenv
load_dotenv()

def parse_request_body(request):
    try:
        body_unicode = request.body.decode('utf-8')         # декодируем
        parsed_data = urllib.parse.parse_qs(body_unicode)   # переводим в словарь параметров

        number = parsed_data['From'][0]                     # отправитель сообщения
        original_text = parsed_data['Body'][0]              # текст входящего сообщения
        user = parsed_data['ProfileName'][0]                # Имя клиента в whatsapp аккаунте

    except (UnicodeDecodeError, KeyError, IndexError):
        response = "Ошибка чтения входящих данных Twilio."
        return HttpResponse(response)

    router = original_text.split()[0].lower().strip()
    if  router in ["осадки", "погода"]:
        handle_precipitation_request(number, original_text, user, router)
    else:
        handle_reminder_request(number, original_text, user)

# Обработка напоминаний
def handle_reminder_request(number, original_text, user):
    reminder_time = extract_date(original_text)
    send_confirmation(number, original_text, reminder_time, None, user)

    reminder_text = text_converting(original_text)
    reminder = save_reminder(reminder_time, original_text,reminder_text)
    save_incoming_message(number, reminder, user)

    process_reminders.delay()

# Обработка входящего сообщения
def handle_precipitation_request(number, original_text, user, router):
    # Достаем имя города
    city = original_text.split()[1:]
    city = ' '.join(city).strip()

    # Сохраняем
    city_id, created = City.objects.get_or_create(name=city)

    # Запрос прогноза либо сохранение в подписчики на уведомления
    if router == 'погода':
        forecast_precipitation(city, user, number)
        Users.objects.create(number=number,user=user,city=city_id,
                            rain_notifications_subscription=False)
    else:
        send_confirmation(number=number, city=city, user=user)
        check_precipitation_and_send_reminders.delay()
        Users.objects.create(number=number, user=user, city=city_id,
                            rain_notifications_subscription=True)


# Распознавание времени из сообщения
def extract_date(message_body):
    try:
        reminder_time = date_parser.parse(message_body, fuzzy_with_tokens=True, fuzzy=True)[0]
        if 'завтра' in message_body.lower():
            return reminder_time + dt.timedelta(days=1)
        if 'послезавтра' in message_body.lower():
            return reminder_time + dt.timedelta(days=2)
        return reminder_time
    except ValueError:
        return None


