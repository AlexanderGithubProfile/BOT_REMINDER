import sys
import logging
import datetime
from dateutil.parser import parse
from aiogram import types, html
from aiogram.types import Message

from dbconnect import city_database, reminder_database
from utils_speech import text_to_speech
from utils_gpt import text_commenting, text_converting
from utils_weather import weather_forecast, forecast_precipitation
from utils_weather import check_precipitation as check_next_2_days
from utils_keyboard import keyboard_trash

from dotenv import load_dotenv
logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
load_dotenv()

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

# Основной модуль извлечения инф из сообщений
async def process_message(message: Message):
    # Предобработка сообщения от пользователя
    number = message.chat.id
    user = message.from_user.full_name
    original_text = message.text
    router = original_text.split()[0].lower().strip()
    header = f'✉️<b> {user} </b><i>&lt;<a href="t. me">@weather_tool_bot </a>&gt;</i>\n\n'

    try:
        if router in ["осадки", "погода"]:
            # Извлекаем и проверяем город
            city = original_text.split()[1:]
            city = ' '.join(city).strip()
            city_data = await forecast_precipitation(city)
            city = city_data['city']['name']
            if city == None:
                await message.answer(f'{header}Похоже в городе опечатка, попробуйте еще :\n/help')

            else:
                if router == 'осадки':
                    # Подписка на предупреждения об осадках
                    await send_confirmation_and_rain_check(message, number, user, city)
                else:
                    # Отправка прогноза погоды
                    forecast = await weather_forecast(city_data, user)
                    await message.answer(f'{forecast}', parse_mode='HTML')
                    await city_database(number, user, city, subscribe=False)

        # Сохранение напоминания
        else:
            await save_reminder_and_send_confirm(message, number, user, original_text, header)

    except TypeError:
        await message.answer(f"{header}Nice try! но что-то пошло не так")
        await message.answer_sticker('CAACAgIAAxkBAAIVwWZIlS0BmEwVcZOsutR5LXIEH8tUAAJjAAPb234AAYydBT3nQoPnNQQ')

# Подтверждение подписки, проверяем прогноз на осадки
async def send_confirmation_and_rain_check(message, number, user, city):
    header = f'✉️<b> {user} </b><i>&lt;<a href="t. me/weather_tool_bot">@weather_tool_bot </a>&gt;</i>\n\n'
    confirm_text = (f"{header}Готово! Вы подписаны на уведомления об осадках в г.{html.bold(city)}")
    await message.answer(confirm_text, parse_mode='HTML')
    await city_database(number, user, city, subscribe=True)
    await message.answer(await check_next_2_days(city))

# Напоминание. Сохраняем и высылаем подтверждение
async def save_reminder_and_send_confirm(message, number, user, original_text, header):
    reminder_time = await extract_date(original_text)
    if reminder_time is not None:
        text_ = (f'{header}Ок напоминание на <b>{reminder_time.strftime("%H:%M %d.%m.%y")}</b> установлено')
        await message.answer(text=text_, parse_mode='HTML', reply_markup=keyboard_trash)

        # Высылаем голосовое сообщение
        if 'голос' in original_text:
            await message.answer_sticker('CAACAgIAAxkBAAIB0WY8i8xLGVkIt2j-6nA-2oF62YiQAAJfAAPb234AAYSwVJsRrsrjNQQ')
            comment = await text_commenting(message.text)
            await text_to_speech(comment)
            await message.answer_voice(types.FSInputFile('assets/output.mp3'), caption=f'{header}{comment}')

        # Преобразования текста в напоминание
        reminder_text = await text_converting(original_text)
        await reminder_database(reminder_time, original_text, reminder_text, number, user)
    else:
        await message.answer(f"{header}Не указано время напоминания")
        await message.answer_sticker('CAACAgIAAxkBAAICDWY8j4zOOlL2N2_3ojI - oNjFZ7dcAAJjAAPb234AAYydBT3nQoPnNQQ')

