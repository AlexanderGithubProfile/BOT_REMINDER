from django.db import models

# Модель для хранения напоминаний к отправке
class Reminder(models.Model):
    # Модель для хранения напоминаний
    reminder_time = models.DateTimeField()  # Время напоминания
    recieved_time = models.DateTimeField(auto_now_add=True)
    original_text = models.TextField(blank=True)
    reminder_text = models.TextField()       # Текст напоминания
    sent = models.BooleanField(default=False)  # Флаг отправки напоминания


    def __str__(self):
        return self.reminder_text

# Модель для хранения городов
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

# Модель для хранения контактных данных
class Users(models.Model):
    number = models.CharField(max_length=100)
    user = models.CharField(max_length=100, null=True)    # Отправитель сообщения
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='messages', null=True)  # Внешний ключ для связи с городом
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    rain_notifications_subscription = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
