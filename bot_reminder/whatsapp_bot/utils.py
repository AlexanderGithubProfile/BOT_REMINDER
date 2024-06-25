import sys
import logging
import urllib.parse

import datetime as dt
from .models import City, Users
from django.http import HttpResponse
from .twilio import send_confirmation
from dateutil import parser as date_parser
from .gpt_responder import text_converting
from .weather import forecast_precipitation

from django.http import HttpResponse, HttpRequest
from .tasks import process_reminders, check_precipitation_and_send_reminders
from .services import save_incoming_message, save_reminder
from typing import Any, Dict, Tuple, Optional

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
from dotenv import load_dotenv
load_dotenv()

def parse_request_body(request: HttpRequest) -> HttpResponse:
    """Достаем данные из сообщения от Twilio(whatsapp)"""
    try:
        body_unicode: str = request.body.decode('utf-8')         # декодируем
        parsed_data: Dict[str, Any] = urllib.parse.parse_qs(body_unicode)   # переводим в словарь параметров

        number: str = parsed_data['From'][0]                     # отправитель сообщения
        original_text: str = parsed_data['Body'][0]              # текст входящего сообщения
        user: str = parsed_data['ProfileName'][0]                # Имя клиента в whatsapp аккаунте

    except (UnicodeDecodeError, KeyError, IndexError):
        response = "Ошибка чтения входящих данных Twilio."
        return HttpResponse(response)

    router = original_text.split()[0].lower().strip()
    if  router in ["осадки", "погода"]:
        handle_precipitation_request(number, original_text, user, router)
    else:
        handle_reminder_request(number, original_text, user)

# Обработка напоминаний
def handle_reminder_request(number: str, original_text: str, user: str) -> None:
    reminder_time: Optional[dt.datetime] = extract_date(original_text)
    send_confirmation(number, original_text, reminder_time, None, user)

    reminder_text: str = text_converting(original_text)
    reminder = save_reminder(reminder_time, original_text, reminder_text)
    save_incoming_message(number, reminder, user)

    process_reminders.delay()

def handle_precipitation_request(number: str, original_text: str, user: str, router: str) -> None:
    """Обработка входящего сообщения"""
    # Достаем имя города
    city: str = ' '.join(original_text.split()[1:]).strip()

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
def extract_date(message_body: str) -> Optional[dt.datetime]:
    try:
        reminder_time: dt.datetime = date_parser.parse(message_body, fuzzy_with_tokens=True, fuzzy=True)[0]
        if 'завтра' in message_body.lower():
            return reminder_time + dt.timedelta(days=1)
        if 'послезавтра' in message_body.lower():
            return reminder_time + dt.timedelta(days=2)
        return reminder_time
    except ValueError:
        return None


