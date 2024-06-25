import asyncio
from aiogram import Bot, html, types
from utils_base import extract_date

# Отправки демо-оповещения о вероятности осадков
async def send_notification_about_precipitation(bot: Bot, sender: int) -> None:
    message_content = """⚠️<b> Warning осадки <a href='t.me/weather_tool_bot'>г.Москва</a>: </b>\nВероятность осадков 99.5% с 15:00 до 21:00, не забудьте зонт !
\n\nБудет небольшой снег, температура -1.0°C:   
•   <b>15:00-18:00</b> вероятность : 100% 
•   <b>18:00-21:00</b> вероятность : 99.0% """
    await bot.send_message(chat_id=sender, parse_mode='HTML', text=message_content)

# Функция демонстрации режима работы бота - напоминание
async def send_reminder(bot: Bot, sender: int, full_name: str) -> None:
    example_text = '<b>Привет! Это твой напоминатель. Не забудь купить зубную пасту сегодня вечером в 19:00!</b>'
    header = f'✉️<b> {full_name} </b><i>&lt;<a href="t.me/weather_tool_bot">@weather_tool_bot </a>&gt;</i>\n\n'
    await bot.send_message(chat_id=sender, text=f'{header}{example_text}', parse_mode='HTML')

# Функция демонстрации режима работы бота - оповещение об осадках
async def demo(text: str, sender: int, message: types.Message, full_name: str, bot: Bot) -> None:
    await message.answer(f'{html.italic("К примеру " + full_name)}:  \n -        ' + text)
    if 'осадки' in text.lower():
        await asyncio.sleep(1)
        await message.answer(f'{html.code("... это оповещение об осадках ...")}')
        await asyncio.sleep(1)
        await send_notification_about_precipitation(bot, sender)
    else:
        await asyncio.sleep(1)
        await message.answer(f'{html.code("...... это напоминание ......")}')
        await asyncio.sleep(1)
        await send_reminder(bot, sender, full_name)
