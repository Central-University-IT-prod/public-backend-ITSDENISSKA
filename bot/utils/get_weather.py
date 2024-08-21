import datetime

import requests

from bot.data.settings import settings


def get_weather(lat: str, lon: str, date: str) -> str:
    try:
        date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        timedelta = date - datetime.date.today()
        if timedelta.days > 14 or timedelta.days < 1:
            return "😔Прогноз погоды доступен только на 14 дней вперёд"
        data = {
            "key": settings.bots.api_weather,
            "q": f"{lat},{lon}",
            "days": timedelta.days,
            "lang": "ru",
        }
        response = requests.post('http://api.weatherapi.com/v1/forecast.json', data=data)
        info = response.json()['forecast']['forecastday'][-1]['day']
        message = (f'🌦️Погода на {str(date.day).rjust(2, "0")}.{str(date.month).rjust(2, "0")}.{date.year}\r\n\n'
                   f'🌡Температура: {info['avgtemp_c']}°C\n'
                   f'🌬️Скорость ветра: {info['avgvis_km']} км/ч\n'
                   f'⛈️Ожидается: {info['condition']['text']}')
        return message
    except:
        return "😔Произошла ошибка на сервере"
