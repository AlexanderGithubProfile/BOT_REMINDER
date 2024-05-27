# Используем официальный образ Python
FROM python:3.12-slim

# Отключаем кеширование внутри контейнеров и буферизацию для логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости для postgres
RUN apt-get update && apt-get install -y gcc libpq-dev

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Выполняем команды миграции и создаем суперпользователя (опционально)
CMD python manage.py migrate \
    #&& python manage.py shell -c "from django.contrib.auth import get_user_model;User = get_user_model();if not User.objects.filter(username='admin').exists():User.objects.create_superuser('admin', 'admin@example.com', 'admin')" \
    && python manage.py collectstatic --no-input \
    && gunicorn bot_reminder.wsgi:application --bind 0.0.0.0:8000 --log-level info

