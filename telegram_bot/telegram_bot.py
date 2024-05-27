import os
import asyncio
import logging
import sys

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, html
from aiogram.types.message import Message
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties

from utils_demo import demo
from utils_base import process_message
from utils_keyboard import keyboard_help, keyboard_start
from dotenv import load_dotenv
load_dotenv()
dp = Dispatcher()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Стартовый
@dp.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await message.answer_sticker('CAACAgIAAxkBAAIBwWY8iur1NohWGW1_lKvUC94E2PSwAAJuAAPb234AAUaeZ3EyOf6TNQQ')
    await message.answer(text=f"<b>ПРИВЕТ {message.from_user.full_name.upper()}, ЭТО REMINDER_BOT</b>\nЯ помогу не пропустить важные события и сообщу если ожидается дождь 🌨🌨🌨 ",
                         reply_markup=keyboard_start,
                         parse_mode=ParseMode.HTML)
@dp.message(Command('help'))
async def help_handler(message: Message, bot: Bot) -> None:
    keyboard = keyboard_help
    await message.answer_sticker('CAACAgIAAxkBAAICxGY8nOuWnIRXGXdlHaNIEFqTpzaVAAI_AAPb234AAfTmnDgB5KppNQQ')
    await message.answer(
        text=f"<b>Это пример использования :</b>\n-    Установите напоминание и его время\n-    Подпишитесь на рассылку о дожде в форме<b>: 'осадки Москва'</b> ",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML)

# Кнопка 'info'
@dp.message(Command('info'))
async def info_handler(message: Message, bot: Bot) -> None:
    await message.answer_photo(types.FSInputFile(path='1.png'),
                               caption=f'{html.bold("GITHUB :")}\ngithub.com/AlexanderGithubProfile/WHATSAPP_BOT_REMINDER\n\n{html.bold("TELEGRAM :")}\n@weather_tool_bot \n(https://t.me/weather_tool_bot)')

# Основной модуль обработки сообщений
@dp.message()
async def echo_handler(message: Message) -> None:
    await process_message(message)

# Реакция на кнопки "info"
@dp.callback_query(lambda query: query.data == 'info')
async def info_handler(query: types.CallbackQuery):
    await query.message.answer_photo(types.FSInputFile(path='1.png'),
                                     caption=f'{html.bold("GITHUB :")}\ngithub.com/AlexanderGithubProfile/WHATSAPP_BOT_REMINDER\n\n{html.bold("TELEGRAM :")}\n@weather_tool_bot \n(https://t.me/weather_tool_bot)')

# Реакция на кнопки "пример команд"
@dp.callback_query(lambda query: query.data == 'command_example')
async def command_example_handler(query: types.CallbackQuery):
    await help_handler(query.message, query.bot)

# Реакция на кнопки выбора в примерах команд
@dp.callback_query(lambda query: query.data in ['reminder', 'precipitation'])
async def command_example_handler(query: types.CallbackQuery, bot: Bot):
    # Определяем индекс и получаем текст кнопки, вызываем реакцию
    a = 0 if query.data == 'reminder' else 1
    button_text = query.message.reply_markup.inline_keyboard[0][a].text.lstrip('Вы :')
    await demo(text=button_text,sender=query.from_user.id,
               message=query.message,full_name=query.from_user.full_name,
               bot=bot)

async def main() -> None:
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())