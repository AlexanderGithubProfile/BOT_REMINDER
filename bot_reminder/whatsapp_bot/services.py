from datetime import datetime
from celery import shared_task
from .models import Users, Reminder

def save_incoming_message(number: str, reminder=None, user: str = None) -> None:
    """Сохраняет входящее сообщение в базу данных."""
    users = Users(number=number, user=user)
    if reminder is not None:
        users.reminder = reminder
    users.save()
@shared_task
def save_reminder(reminder_time: datetime, original_text: str, reminder_text: str) -> Reminder:
    """Сохраняет напоминание в базу данных."""
    reminder = Reminder(reminder_time=reminder_time,
                        original_text=original_text,
                        reminder_text=reminder_text)
    reminder.save()
    return reminder