from celery import shared_task
from .models import Users, Reminder

def save_incoming_message(number, reminder=None, user=None):
    users = Users(number=number, user=user)
    if reminder is not None:
        users.reminder = reminder
    users.save()
@shared_task
def save_reminder(reminder_time, original_text, reminder_text):
    reminder = Reminder(reminder_time=reminder_time,
                        original_text=original_text,
                        reminder_text=reminder_text)
    reminder.save()
    return reminder