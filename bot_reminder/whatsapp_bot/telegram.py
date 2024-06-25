import os
from aiogram import Bot
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# Отправка через Celery-планировщика пользователям из базы данных
async def telegram_sender(number: str, reminder_text: str, reminder_time: Optional[str] = None, name: Optional[str] = None) -> None:
    async with Bot(token=os.getenv('TELEGRAM_TOKEN')) as bot:
        if reminder_time is None:
            await bot.send_message(chat_id=number,
                                    parse_mode='HTML',
                                    text=reminder_text)
        else:
            header = f'✉️<b> {name} </b><i>&lt;<a href="t. me/weather_tool_bot">@weather_tool_bot </a>&gt;</i>\n\n'
            formatted_html = (f'{header}<b>{reminder_text}</b>')
            await bot.send_message(chat_id=number,
                                    parse_mode='HTML',
                                    text=formatted_html)