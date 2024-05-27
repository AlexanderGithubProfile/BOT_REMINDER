import os
import requests
import numpy as np
from datetime import timedelta
from datetime import datetime
from .twilio import send_reminders

# Модуль провверки возможных осадков для списка подписанных на уведомления(НАЧАЛО)
def check_precipitation(city_name):
    try:
        open_weather_token = os.getenv('OPEN_WEATHER_MAP_API')
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&cnt=20&lang=ru&appid={open_weather_token}"
        response = requests.get(url)
        reminder_str_telegram, reminder_str_whatsapp, rain_probabilities = weather_data_extractor(response.json())
        return reminder_str_telegram, reminder_str_whatsapp, rain_probabilities
    except Exception as e:
        print(f'Ошибка: {e}')

# Модуль провверки возможных осадков для списка подписанных на уведомления(ПРОДОЛЖЕНИЕ)
def weather_data_extractor(data):
    # Делаем флаги для суммирования смежных временных промежутков прогнозов
    rain_forecast = False       # Флаг для отслеживания прогноза дождя
    rain_start_time = None      # Время начала прогноза дождя
    rain_end_time = None        # Время окончания прогноза дождя
    total_feels_like = 0        # Общая температура для прогноза дождя
    rain_count = 0              # Количество прогнозов дождя
    rain_probabilities = []
    reminder_str_telegram = ''
    reminder_str_whatsapp = ''
    for i in data['list']:
        if i['pop'] * 100 > 50: # Проверка вероятность дождя больше 50% ?
            if not rain_forecast:
                # Если начался новый прогноз дождя
                rain_start_time = datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S')
                rain_forecast = True
                total_feels_like = i['main']['feels_like']
                rain_count = 1
                rain_probabilities = []  # Список для вероятностей дождя в каждом временном промежутке
            else:  # Продолжение прогноза дождя
                total_feels_like += i['main']['feels_like']
                rain_count += 1
            rain_probabilities.append((i['pop'] * 100, datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S')))
        else:  # Если дождь закончился
            if rain_forecast:
                rain_end_time = datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S')
                average_feels_like = total_feels_like / rain_count
                average_probabilities = np.mean([x[0] for x in rain_probabilities])
                reminder_str_telegram = f"<b>⚠️Warning <a href='http://t.me/weather_tool_bot'>г.{data['city']['name']}</a></b>\nВероятность осадков: {average_probabilities}% с {rain_start_time.strftime('%H:%M')} до {rain_end_time.strftime('%H:%M')}, не забудьте зонт, хорошего дня!\n\nБудет {i['weather'][0]['description']}, температура {np.round(average_feels_like)}°C:"
                reminder_str_whatsapp = f"\n*⚠️Warning* *г.{data['city']['name']}*\nВероятность осадков: {np.round(average_probabilities,1)}% с *{rain_start_time.strftime('%H:%M')}* до *{rain_end_time.strftime('%H:%M')}*, не забудьте зонт, хорошего дня!\n\nБудет {i['weather'][0]['description']}, температура {np.round(average_feels_like)}°C:"
                for prob, time in rain_probabilities:
                    reminder_str_telegram += f"<b>\n•   {time.strftime('%H:%M')}-{(time + timedelta(hours=3)).strftime('%H:%M')}</b> вероятность : {np.round(prob, 1)}%"
                    reminder_str_whatsapp += f"\n•   *{time.strftime('%H:%M')}*-*{(time + timedelta(hours=3)).strftime('%H:%M')}* вероятность : {np.round(prob, 1)}%"
                rain_forecast = False
    return reminder_str_telegram, reminder_str_whatsapp, rain_probabilities

def forecast_precipitation(city, user, number):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&cnt=56&lang=ru&appid={os.getenv('OPEN_WEATHER_MAP_API')}"
    response = requests.get(url).json()
    if response['cod'] == '404':
        return None
    _text = weather_forecast(response, user)
    send_reminders(f'{_text}', number)

def weather_forecast(response, user):
    # Словарь для хранения температур, вероятности дождя и иконок погоды по дням
    daily_data = {}
    header = f'*☀️{user}*<_@weather_tool_bot_>\n\n'
    weekday_names = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }

    # Словарь соответствия значений 'icon' и смайликов
    weather_icons = {
        '01': '☀️',  # ясно
        '02': '🌤️',  # небольшая облачность
        '03': '☁️',  # облачно
        '04': '☁️',  # облачно
        '09': '🌧️',  # легкий дождь
        '10': '🌧️',  # дождь
        '11': '⛈️',  # гроза
        '13': '❄️',  # снег
        '50': '💨'  # туман
    }

    # Итерируемся по списку погодных данных
    for data in response['list']:
        # Извлекаем дату и время из поля 'dt_txt' и преобразуем их в объект datetime
        date_ = datetime.strptime(data['dt_txt'], '%Y-%m-%d %H:%M:%S').date()
        time = datetime.strptime(data['dt_txt'], '%Y-%m-%d %H:%M:%S').time().hour

        temperature = data['main']['temp']
        rain_probability = data['pop']
        weather_icon = data['weather'][0]['icon'][:2]
        # Исключаем данные с временем после 23:00 и до 6:00
        if time >= 6 and time < 23:
            # Добавляем данные в список для данного дня
            if date_ not in daily_data:
                daily_data[date_] = {'temperatures': [temperature], 'rain_probabilities': [rain_probability],
                                     'weather_icons': [weather_icon]}
            else:
                daily_data[date_]['temperatures'].append(temperature)
                daily_data[date_]['rain_probabilities'].append(rain_probability)
                daily_data[date_]['weather_icons'].append(weather_icon)

    # Вычисляем среднюю температуру и максимальную вероятность дождя для каждого дня и выводим результат
    for date, data in daily_data.items():
        max_temp = max(data['temperatures'])
        min_temp = min(data['temperatures'])
        # average_temp = sum(data['temperatures']) / len(data['temperatures'])
        max_rain_prob = max(data['rain_probabilities'])
        # Выводим вероятность дождя только если она больше 0%
        if max_rain_prob > 0:
            header += f"{weekday_names[date.weekday()]}: *{min_temp:.0f}°-{max_temp:.0f}°* ({max_rain_prob * 100:.0f}%) {weather_icons[max(data['weather_icons'], key=data['weather_icons'].count)]}\n"
        else:
            header += f"{weekday_names[date.weekday()]}: *{min_temp:.0f}°-{max_temp:.0f}°* {weather_icons[max(data['weather_icons'], key=data['weather_icons'].count)]}\n"
    return header