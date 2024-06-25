import os
from typing import Optional
import datetime as dt
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

# Объявление переменных Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Функция для отправки напоминания
def send_reminders(reminder_text: str, number: str, user: Optional[str] = None) -> None:
    # Инициализация клиента Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    if user is not None:
        header = f'*✉️{user}*<_@weather_tool_bot_>\n'
    else:
        header = ''
    try:
        # Отправка сообщения WhatsApp
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=f'{header} {reminder_text}',
            to=number
            )
    except Exception as e:
        print(f"Ошибка при отправке напоминания на номер {number}: {str(e)}")

# Функция для отправки подтверждения установки напоминания через Twilio
def send_confirmation(number: str, reminder_text: Optional[str] = None, reminder_time: Optional[dt.datetime] = None, city: Optional[str] = None, user: Optional[str] = None) -> None:
    # Инициализация клиента Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    header = f'*✉️{(user)}*<_@weather_tool_bot_>\n'

    if reminder_text is not None:
        message = client.messages.create(
            body=f"{header}Напоминание *на {reminder_time.strftime('%H:%M %d-%m-%Y')}* установлено.",
            from_=TWILIO_PHONE_NUMBER,
            to=number
        )
    else:
        message = client.messages.create(
            body=f"{header}Вы подписаны на уведомления об осадках в городе *{city}*",
            from_=TWILIO_PHONE_NUMBER,
            to=number
        )