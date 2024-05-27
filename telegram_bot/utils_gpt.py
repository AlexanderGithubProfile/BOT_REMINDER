from g4f.client import AsyncClient



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