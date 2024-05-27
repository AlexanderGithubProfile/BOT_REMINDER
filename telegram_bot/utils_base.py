import os
import sys
import logging
import requests
import datetime


from dateutil.parser import parse
from g4f.client import AsyncClient

from aiogram import types, html
from aiogram.types import Message, InlineKeyboardButton
from weather import weather_forecast
from dbconnect import city_database, reminder_database
from utils_keyboard import keyboard_trash
from dotenv import load_dotenv
from weather import check_precipitation as check
logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
load_dotenv()

# Функция комментирования ботом напоминания пользователя
async def text_commenting(prompt_text):
    client = AsyncClient()
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",

        messages=[{"role": "user", "content": f'''Представь что ты бот напоминатель если тебе был запрос 
                                                "{prompt_text.rstrip('голос')}" 
                                                Тебе нужно прокомментировать это с юмором, при этом коротко, начни с "Круто,будем" и закончи комментарий "если ты понимаешь о чем я"'''}],
    )
    text = response.choices[0].message.content
    if not text.strip():
        return await text_commenting(prompt_text)
    else:
        return text

# Функция преобразования текста напоминания в форму напоминания
async def text_converting(prompt_text):
    client = AsyncClient()
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",

        messages=[{"role": "user", "content": f'''Представь что ты бот напоминатель если тебе был запрос 
                                                "{prompt_text}" 
                                                какое ты выведешь сообщение в день напоминания, начни ответ "Привет! Это твой напоминатель. Не забудь"'''}],
)
    text = response.choices[0].message.content
    if not text.strip():
        return await text_commenting(prompt_text)
    else:
        return text

# Распознавание времени
async def extract_date(message_body):
    try:
        reminder_time = parse(message_body, fuzzy_with_tokens=True,fuzzy=True)[0]
        if 'завтра' in message_body.lower():
            return reminder_time + datetime.timedelta(days=1)
        if 'послезавтра' in message_body.lower():
            return reminder_time + datetime.timedelta(days=2)
        return reminder_time
    except ValueError:
        return None

# Проверка вероятности осадков
async def check_precipitation(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&cnt=20&lang=ru&appid={os.getenv('OPEN_WEATHER_MAP_API')}"
    response = requests.get(url).json()
    if response['cod'] == '404':
        return None
    return response

# Преобразования голоса
async def text_to_speech(text):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": "0bdbcf63934856091cef9ee133b1339f"
    }

    data = {
      "text": text,
      "model_id": "eleven_multilingual_v2",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "speaker_boost": True
      }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# Основной модуль обработки сообщений
async def process_message(message: Message):
    # Предобработка сообщения от пользователя
    number = message.chat.id
    user = message.from_user.full_name
    original_text = message.text
    router = original_text.split()[0].lower().strip()
    header = f'✉️<b> {user} </b><i>&lt;<a href="t. me/weather_tool_bot">@weather_tool_bot </a>&gt;</i>\n\n'

    # Обработка запроса прогноза погоды или подписки на осадки
    try:
        if router in ["осадки", "погода"]:
            city = original_text.split()[1:]
            city = ' '.join(city).strip()

            # Есть ли ошибка названия города
            city_data = await forecast_precipitation(city)
            city = city_data['city']['name']
            if city == None:
                await message.answer(f'{header}Похоже в городе опечатка, попробуйте еще :\n/help')
            else:
                if router == 'осадки':


                    # Подтверждение подписки
                    await confiramtion(message, number, user, city)
                    await message.answer(await check(city))
                else:
                    # Отправка прогноза погоды
                    forecast = await weather_forecast(city_data, user)
                    await message.answer(f'{forecast}', parse_mode='HTML')
                    await city_database(number, user, city, subscribe=False)


        # Обработка напоминаний
        else:
            reminder_time = await extract_date(original_text)
            if reminder_time is not None:
                formatted_html = (f'{header}Ок напоминание на <b>{reminder_time.strftime("%H:%M %d.%m.%y")}</b> установлено')
                await message.answer(text=formatted_html,
                                     parse_mode='HTML',
                                     reply_markup=keyboard_trash)
                # Опция для голосового ответа
                if 'голос' in original_text:
                    await message.answer_sticker('CAACAgIAAxkBAAIB0WY8i8xLGVkIt2j-6nA-2oF62YiQAAJfAAPb234AAYSwVJsRrsrjNQQ')
                    comment = await text_commenting(message.text)
                    await text_to_speech(comment)
                    await message.answer_voice(types.FSInputFile('output.mp3'),caption=f'{header}{comment}')

                # Преобразования текста из оригинального в напоминание
                reminder_text = await text_converting(original_text)
                await reminder_database(reminder_time, original_text, reminder_text, number, user)
            else:
                await message.answer(f"{header}Не указано время напоминания")
                await message.answer_sticker('CAACAgIAAxkBAAICDWY8j4zOOlL2N2_3ojI - oNjFZ7dcAAJjAAPb234AAYydBT3nQoPnNQQ')

    except TypeError:
        await message.answer(f"{header}Nice try! но что-то пошло не так")
        await message.answer_sticker('CAACAgIAAxkBAAIVwWZIlS0BmEwVcZOsutR5LXIEH8tUAAJjAAPb234AAYydBT3nQoPnNQQ')

# Отправка уведомление с подтверждением
async def confiramtion(message, number, user, city):
    header = f'✉️<b> {user} </b><i>&lt;<a href="t. me/weather_tool_bot">@weather_tool_bot </a>&gt;</i>\n\n'
    confiramtion = (f"{header}Готово! Вы подписаны на уведомления об осадках в г.{html.bold(city)}")
    await message.answer(confiramtion, parse_mode='HTML')
    await city_database(number, user, city, subscribe=True)

# API запрос к сервису погоды
async def forecast_precipitation(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&cnt=56&lang=ru&appid={os.getenv('OPEN_WEATHER_MAP_API')}"
    response = requests.get(url).json()
    if response['cod'] == '404':
        return None
    return response

