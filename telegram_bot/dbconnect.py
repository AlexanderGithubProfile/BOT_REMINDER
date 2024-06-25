# Добавление записи напоминания
import os
import asyncpg
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Добавление записи города для оповещений об осадках
async def city_database(number: int, user: str, city: str, subscribe: bool = True) -> None:
    conn = await asyncpg.connect(user=os.getenv('DB_USER'),
                                 password=os.getenv('DB_PASS'),
                                 database=os.getenv('DB_NAME'),
                                 port=os.getenv('DB_PORT'),
                                 command_timeout=60,
                                 host=os.getenv('DB_HOST'))
    try:
        async with conn.transaction():
            # Проверяем есть ли город и делаем его запись, возвращаем внешний ключ записи
            city_id = await conn.fetchval("SELECT id FROM whatsapp_bot_city WHERE name = $1", city)
            if city_id is None:
                city_id = await conn.fetchval(
                    "INSERT INTO whatsapp_bot_city (name) VALUES ($1) RETURNING id", city)

            # Вставляем сообщение и внешний ключ города
            query = "INSERT INTO whatsapp_bot_users (number, \"user\", rain_notifications_subscription, city_id) VALUES ($1, $2, $3, $4)"
            await conn.execute(query, str(number), str(user), subscribe, city_id)

    finally:
        await conn.close()

# Добавление записи напоминания
async def reminder_database(reminder_time: datetime, original_text: str, reminder_text: str, number: int, user: str) -> None:
    conn = await asyncpg.connect(user=os.getenv('DB_USER'),
                                 password=os.getenv('DB_PASS'),
                                 database=os.getenv('DB_NAME'),
                                 port=os.getenv('DB_PORT'),
                                 command_timeout=60,
                                 host=os.getenv('DB_HOST'))
    try:
        # Устанавливаем часовой пояс по умолчанию
        #await conn.execute("SET TIME ZONE 'Asia/Manila'")

        async with conn.transaction():
            # Делаем внешний ключ
            reminder_id = await conn.fetchval(
                "INSERT INTO whatsapp_bot_reminder (original_text, recieved_time, reminder_time, reminder_text, sent) "
                "VALUES ($1, NOW(), $2, $3, False) RETURNING id",
                original_text, reminder_time, reminder_text)

            query = "INSERT INTO whatsapp_bot_users (number, \"user\", rain_notifications_subscription, reminder_id) VALUES ($1, $2, $3, $4)"
            await conn.execute(query, str(number), str(user), False, reminder_id)
    finally:
        await conn.close()