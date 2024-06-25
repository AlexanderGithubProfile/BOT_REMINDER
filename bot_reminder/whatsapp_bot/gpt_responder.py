from g4f.client import Client as G4FClient


def text_converting(prompt_text: str) -> str:
    """Конвертирует текст запроса в ответ бота, используя GPT."""
    client = G4FClient()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f'''Представь что ты бот напоминатель если тебе был запрос 
                                                "{prompt_text}" 
                                                какое ты выведешь сообщение в день напоминания, начни ответ "Привет! Это твой напоминатель. Не забудь"'''}],
    )
    reminder_text = response.choices[0].message.content

    # Если сервис GPT не ответил повтор запроса
    if not reminder_text.strip():
        return text_converting(prompt_text)
    else:
        return reminder_text