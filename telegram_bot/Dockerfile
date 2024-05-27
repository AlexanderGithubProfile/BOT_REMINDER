FROM python:3.12-slim

# Отключаем кеширование внутри контейнеров и буферизацию для логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app/
#ADD . .
RUN pip install -r requirements.txt

CMD python telegram_bot.py