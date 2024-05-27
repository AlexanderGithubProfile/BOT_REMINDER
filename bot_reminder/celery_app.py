import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_reminder.settings')

app = Celery('whatsapp_bot')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.broker_connection_retry_on_startup = True
app.conf.beat_schedule = {
    'send-reminders-every-minute': {
        'task': 'whatsapp_bot.tasks.process_reminders',
        'schedule': 60.0,
    },
    'check_precipitation_and_send_reminders': {
        'task': 'whatsapp_bot.tasks.check_precipitation_and_send_reminders',
        'schedule': crontab(hour=6, minute=00),
    },
}

app.autodiscover_tasks()
app.conf.timezone = 'Asia/Manila'
